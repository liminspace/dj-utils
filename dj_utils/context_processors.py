# coding=utf-8
from __future__ import absolute_import
from dj_utils import settings as u_settings
from dj_utils.http import full_url


def email_default(request=None):
    """
    Default context for render email templates.
    """
    return {
        'SITE_DOMAIN': u_settings.SITE_DOMAIN,
        'DOMAIN_TITLE': u_settings.DOMAIN_TITLE,
        'HOMEPAGE_URL': full_url,
    }
