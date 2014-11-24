# coding=utf-8
from __future__ import absolute_import
import re
from django import forms
from django.db import models
from django.utils.translation import ugettext_lazy as _
from dj_utils.validators import validate_phone_number12


class PhoneNumberFormField(forms.CharField):
    default_validators = [validate_phone_number12]
    re_clean = re.compile(r'[\s\(\)\-]+')

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 22
        super(PhoneNumberFormField, self).__init__(*args, **kwargs)

    def clean(self, value):
        value = self.re_clean.sub('', self.to_python(value))
        return super(PhoneNumberFormField, self).clean(value)


class PhoneNumberField(models.CharField):
    description = _('Phone number')

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 22
        super(PhoneNumberField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {'form_class': PhoneNumberFormField}
        defaults.update(kwargs)
        return super(PhoneNumberField, self).formfield(**defaults)
