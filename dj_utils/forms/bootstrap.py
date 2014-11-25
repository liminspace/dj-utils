# coding=utf-8
from __future__ import absolute_import
from django import forms
from dj_utils.forms.helpers import add_css_class_to_fields_widget


class BootstrapForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(BootstrapForm, self).__init__(*args, **kwargs)
        add_css_class_to_fields_widget(self.fields, 'form-control')


class BootstrapModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BootstrapModelForm, self).__init__(*args, **kwargs)
        add_css_class_to_fields_widget(self.fields, 'form-control')
