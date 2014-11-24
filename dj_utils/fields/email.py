# coding=utf-8
from __future__ import absolute_import
from django.db import models
from django.utils.translation import ugettext_lazy as _


class NullableEmailField(models.EmailField):
    description = _(u'EmailField that stores NULL but returns empty string')
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        kwargs['null'] = True
        kwargs['blank'] = True
        super(NullableEmailField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if isinstance(value, models.EmailField):
            return value
        return value or ''

    def get_prep_value(self, value):
        return value or None
