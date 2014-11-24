# coding=utf-8
from __future__ import absolute_import
import urllib
import hashlib
from dj_utils import settings as u_settings


def get_ava_url(email, size=None):
    if not size:
        size = u_settings.GRAVATAR_DEFAULT_SIZE
    return "%s://www.gravatar.com/avatar/%s?%s" % (
        (u_settings.GRAVATAR_SECURE and 'https' or 'http'),
        hashlib.md5(email.lower()).hexdigest(),
        urllib.urlencode({'d': u_settings.GRAVATAR_DEFAULT_IMAGE, 's': str(size), 'r': u_settings.GRAVATAR_RATING})
    )


def get_profile_url(email):
    return "%s://ru.gravatar.com/%s" % ((u_settings.GRAVATAR_SECURE and 'https' or 'http'),
                                        hashlib.md5(email.lower()).hexdigest())
