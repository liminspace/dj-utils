# coding=utf-8
from __future__ import absolute_import
from django.shortcuts import _get_queryset


def get_object_or_None(klass, *args, **kwargs):
    """
    Uses get() to return an object or None if the object does not exist.
    klass may be a Model, Manager, or QuerySet object.
    All other passed arguments and keyword arguments are used in the get() query.
    """
    queryset = _get_queryset(klass)
    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        return None


def chunked_qs(qs, chunksize=100):
    total = qs.count()
    for start in xrange(0, total, chunksize):
        for t in qs[start:min(start + chunksize, total)]:
            yield t
