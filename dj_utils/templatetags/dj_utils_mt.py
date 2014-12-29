# coding=utf-8
from __future__ import absolute_import
from django import template
from django.conf import settings
from django.utils import html
from django.utils.safestring import mark_safe
from dj_utils.settings import LANGUAGES_CODES


register = template.Library()


# Example usage:
#
# <script>
#   function modeltranslation_form_fixer(form){
#     $("[data-lang-default='1']", form).each(function(){
#       var t = $(this);
#       $('#' + t.data('lang-copy-to-id')).val($('#' + t.data('lang-copy-from-id')).val())
#     });
#   }
#
#   $(function(){
#     $('#my-form').submit(function(){
#       modeltranslation_form_fixer(this);
#     });
#   });
# </script>
#
#
# <form id="my-form">
#   {{ form.name|hide_mt_field }}
#   {% for field in form|get_mt_fields:'name' %}
#     <div class="form-group" {{ field.data_attrs }}>
#       <label class="control-label" for="{{ field.auto_id }}">
#         {{ field.label }}:
#       </label>
#       <div class="controls">
#         {{ field }}
#       </div>
#     </div>
#   {% endfor %}
# </form>


@register.filter
def get_mt_fields(value, arg):
    base_field, n = value[arg], 0
    for lang in LANGUAGES_CODES:
        try:
            field = value['%s_%s' % (arg, lang)]
            field.data_attrs = mark_safe(
                'data-lang="%(lang)s" data-lang-default="%(default)s" '
                'data-lang-copy-to-id="%(cti)s" data-lang-copy-from-id="%(cfi)s"' % {
                    'lang': lang,
                    'default': int(lang == settings.LANGUAGE_CODE),
                    'cti': base_field.auto_id,
                    'cfi': field.auto_id,
                }
            )
        except KeyError:
            field = None
            n += 1
        if field is not None:
            yield field
    if n == len(LANGUAGES_CODES):
        yield base_field


@register.assignment_tag
def translate_mt_field(form, field_name, lang):
    try:
        base_field = form[field_name]
        field = form['%s_%s' % (field_name, lang)]
    except KeyError:
        return None
    field.data_attrs = mark_safe(
        'data-lang="%(lang)s" data-lang-default="%(default)s" '
        'data-lang-copy-to-id="%(cti)s" data-lang-copy-from-id="%(cfi)s"' % {
            'lang': lang,
            'default': int(lang == settings.LANGUAGE_CODE),
            'cti': base_field.auto_id,
            'cfi': field.auto_id,
        }
    )
    return field


@register.filter
def hide_mt_field(value):
    return mark_safe(u'<input type="hidden" id="%s" name="%s" value="%s">' % (
        html.escape(value.auto_id), html.escape(value.name), html.escape(value.form.initial.get(value.name, '')))
    )
