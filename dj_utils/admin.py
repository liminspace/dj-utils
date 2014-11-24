# coding=utf-8
from __future__ import absolute_import
from django.conf import settings


class TranslationAdminMedia:
    class Media:
        js = (
            '%smodeltranslation/js/force_jquery.js' % settings.STATIC_URL,
            '%sdj_utils/js/jquery-ui-1.10.4.custom.min.js' % settings.STATIC_URL,
            '%smodeltranslation/js/tabbed_translation_fields.js' % settings.STATIC_URL,
        )
        css = {
            'screen': ('%smodeltranslation/css/tabbed_translation_fields.css' % settings.STATIC_URL,),
        }
