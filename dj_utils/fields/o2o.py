from django.db.models import OneToOneField
from django.db.models.fields.related import SingleRelatedObjectDescriptor
from django.db.transaction import atomic


class AutoSingleRelatedObjectDescriptor(SingleRelatedObjectDescriptor):
    @atomic
    def __get__(self, instance, instance_type=None):
        model = getattr(self.related, 'related_model', self.related.model)
        try:
            return super(AutoSingleRelatedObjectDescriptor, self).__get__(instance, instance_type)
        except model.DoesNotExist:
            obj = model(**{self.related.field.name: instance})
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
