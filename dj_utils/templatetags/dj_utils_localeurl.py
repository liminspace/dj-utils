# coding=utf-8
from __future__ import absolute_import
from django import template
from django.conf import settings
from localeurl.utils import strip_script_prefix, strip_path, locale_url
from dj_utils.http import full_url


register = template.Library()


def change_locale_url(url, locale, make_full_url=True):
    """
    Change url to url with stated locale.
    """
    t, path = strip_script_prefix(url)
    t, path = strip_path(path)
    url = locale_url(path, locale)
    if make_full_url:
        url = full_url(url)
    return url


def _current_page_urls(request):
    langs_urls = {}
    for lang in settings.LANGUAGES:
        langs_urls[lang[0]] = change_locale_url(request.get_full_path(), lang[0])
    return langs_urls


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
    langs_urls = _current_page_urls(context['request'])
    return {
        'default_url': langs_urls[settings.LANGUAGE_CODE],
        'langs_urls': langs_urls,
    }
