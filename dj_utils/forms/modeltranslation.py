# coding=utf-8
from __future__ import absolute_import
from django import forms
from django.utils.translation import string_concat, ugettext_lazy as _
from modeltranslation.translator import translator
from modeltranslation.utils import build_localized_fieldname, get_language


def formfield_exclude_translations(db_field, **kwargs):
    """ only non-localized fields """
    if hasattr(db_field, 'translated_field'):
        return None
    if 'field' in kwargs:
        field = kwargs['field']
    else:
        field = db_field.formfield(**kwargs)
    if not field:
        return field
    trans_opts = translator.get_options_for_model(db_field.model)
    if db_field.name in trans_opts.fields:
        field.widget.attrs['class'] = '{0} {1}'.format(
            getattr(field.widget.attrs, 'class', ''),
            'language-depended'
        )
        field.help_text = string_concat(
            field.help_text,
            _(' '),
            _('This field dependent on current language.')
        )
    return field


def formfield_exclude_original(db_field, **kwargs):
    """ only localized fields """
    trans_opts = translator.get_options_for_model(db_field.model)
    if db_field.name in trans_opts.fields:
        return None
    if 'field' in kwargs:
        field = kwargs['field']
    else:
        field = db_field.formfield(**kwargs)
    if hasattr(db_field, 'translated_field'):
        if db_field.name.endswith('_{0}'.format(get_language())):
            field.required = True
        else:
            field.required = False
    return field


def formfield_exclude_irrelevant(db_field, **kwargs):
    """ only localized fields """
    trans_opts = translator.get_options_for_model(db_field.model)
    if db_field.name in trans_opts.fields:
        return None
    if 'field' in kwargs:
        field = kwargs['field']
    else:
        field = db_field.formfield(**kwargs)
    if hasattr(db_field, 'translated_field'):
        if db_field.name.endswith('_{0}'.format(get_language())):
            field.required = True
            field.widget.attrs['class'] = '{0} {1}'.format(
                getattr(field.widget.attrs, 'class', ''),
                'language-depended'
            )
            field.help_text = string_concat(
                field.help_text,
                _(' '),
                _('This field dependent on current language.')
            )
        else:
            return None
    return field


def localize_fieldname(field_name, lang=None):
    if lang is None:
        lang = get_language()
    return build_localized_fieldname(field_name, lang)


class TranslationModelForm(forms.ModelForm):
    def formfield_callback(self, **kwargs):
        return formfield_exclude_translations(self, **kwargs)


class TranslationBulkModelForm(forms.ModelForm):
    def formfield_callback(self, **kwargs):
        return formfield_exclude_original(self, **kwargs)


class TranslationActualModelForm(forms.ModelForm):
    def formfield_callback(self, **kwargs):
        return formfield_exclude_irrelevant(self, **kwargs)
