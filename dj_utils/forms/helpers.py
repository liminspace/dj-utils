# coding=utf-8
from __future__ import absolute_import
from django import forms


BS_FORM_WIDGETS = (forms.TextInput, forms.Textarea, forms.Select, forms.FileInput)


def add_css_class_to_fields_widget(fields, css_class, widget_types=BS_FORM_WIDGETS):
    for k in fields:
        if isinstance(fields[k].widget, widget_types):
            add_css_class_to_field(fields[k], css_class)


def add_css_class_to_field(field, css_class):
    attrs = field.widget.attrs
    if 'class' in attrs:
        if attrs['class']:
            attrs['class'] += ' '
    else:
        attrs['class'] = ''
    attrs['class'] += css_class
