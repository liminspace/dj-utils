# coding=utf-8
from __future__ import absolute_import
from django import template
from django.conf import settings
from dj_utils.http import get_urls_for_langs


register = template.Library()


@register.inclusion_tag('dj_utils/tags/meta_locale_links.html', takes_context=True)
def meta_locale_links(context):
    """
    Outputting meta-tags for the site which has many languages:
        <link rel="alternate" hreflang="x-default" href="http://example.com/">
        <link rel="alternate" hreflang="uk" href="http://example.com/">
        <link rel="alternate" hreflang="ru" href="http://example.com/ru/">
        <link rel="alternate" hreflang="en" href="http://example.com/en/">
    *using django-localeurl
    """
    langs_urls = get_urls_for_langs(context['request'])
    if langs_urls is None:
        return {}
    return {
        'default_url': langs_urls[settings.LANGUAGE_CODE],
        'langs_urls': langs_urls,
    }
