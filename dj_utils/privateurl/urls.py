# coding=utf-8
from __future__ import absolute_import
from django.conf.urls import url
from dj_utils.privateurl.views import privateurl_view


urlpatterns = [
    url(
        r'^(?P<action>[-a-zA-Z0-9_]{1,20})/(?P<token>[-a-zA-Z0-9_]{1,64})$',
        privateurl_view,
        name='dju_privateurl'
    ),
]
