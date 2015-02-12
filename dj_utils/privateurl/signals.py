# coding=utf-8
from __future__ import absolute_import
from django.dispatch import Signal


privateurl_ok = Signal(providing_args=['request', 'obj', 'action'])
privateurl_fail = Signal(providing_args=['request', 'obj', 'action'])
