# coding=utf-8
from __future__ import absolute_import
from django.http.response import Http404
from dj_utils.privateurl.models import PrivateUrl
from dj_utils.privateurl.signals import privateurl_ok, privateurl_fail


def privateurl_view(request, action, token):
    obj = PrivateUrl.objects.get_or_none(action, token)
    if not obj or not obj.is_available():
        results = privateurl_fail.send(PrivateUrl, request=request, obj=obj, action=action)
    else:
        results = privateurl_ok.send(PrivateUrl, request=request, obj=obj, action=action)
        obj.used_counter_inc()
    for receiver, result in results:
        if isinstance(result, dict):
            if 'response' in result:
                return result['response']
    raise Http404
