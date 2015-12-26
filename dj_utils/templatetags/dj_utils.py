# coding=utf-8
from __future__ import absolute_import
from django import template
from dj_utils.upload import make_thumb_url


register = template.Library()


@register.filter
def of_index(value, arg):
    try:
        return value[int(arg)]
    except (IndexError, TypeError, ValueError):
        return ''


@register.filter
def dict_items_sort_by_val(value, arg=None):
    """
    Return items from dict which sorted by value.
    {% for k, v in mydict|dict_items_sort_by_val %}
        ...
    {% endfor %}
    """
    if not isinstance(value, dict):
        return ()
    items = value.items()
    items.sort(key=lambda t: t[1], reverse=bool(arg))
    return items


@register.filter
def dict_items_sort_by_key(value, arg=None):
    """
    Return items from dict which sorted by key.
    {% for k, v in mydict|dict_items_sort_by_key %}
        ...
    {% endfor %}
    """
    if not isinstance(value, dict):
        return ()
    items = value.items()
    items.sort(key=lambda t: t[0], reverse=bool(arg))
    return items


@register.simple_tag(name='make_thumb_url')
def make_thumb_url_(url, label=None, ext=None):
    return make_thumb_url(url, label=label, ext=ext) or url
