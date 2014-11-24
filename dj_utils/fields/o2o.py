# coding=utf-8
from __future__ import absolute_import
from django.db.models import OneToOneField
from django.db.models.fields.related import SingleRelatedObjectDescriptor


class AutoSingleRelatedObjectDescriptor(SingleRelatedObjectDescriptor):
    def __get__(self, instance, instance_type=None):
        try:
            return super(AutoSingleRelatedObjectDescriptor, self).__get__(instance, instance_type)
        except self.related.model.DoesNotExist:
            obj = self.related.model(**{self.related.field.name: instance})
            obj.save()
            return super(AutoSingleRelatedObjectDescriptor, self).__get__(instance, instance_type)


class AutoOneToOneField(OneToOneField):
    """
    OneToOneField creates related object on first call if it doesnt exist yet.
    Use it instead of original OneToOne field.
    Example:
        class MyProfile(models.Model):
            user = AutoOneToOneField(User, primary_key=True)
            ...
    """
    def contribute_to_related_class(self, cls, related):
        setattr(cls, related.get_accessor_name(), AutoSingleRelatedObjectDescriptor(related))
