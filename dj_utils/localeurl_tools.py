# coding=utf-8
from __future__ import absolute_import
from localeurl.utils import strip_script_prefix, strip_path, locale_url
from dj_utils.http import full_url
from django.conf import settings


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


def get_current_page_urls(request):
    langs_urls = {}
    for lang in settings.LANGUAGES:
        langs_urls[lang[0]] = change_locale_url(request.get_full_path(), lang[0])
    return langs_urls
