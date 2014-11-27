# coding=utf-8
from __future__ import absolute_import
import os
from django.conf import settings


USE_HTTPS = getattr(settings, 'USE_HTTPS', False)

UTILS_EMAIL_DEBUG_IN_CONSOLE = getattr(settings, 'UTILS_EMAIL_DEBUG_IN_CONSOLE', True)
UTILS_EMAIL_DEBUG_IN_FILES = getattr(settings, 'UTILS_EMAIL_DEBUG_IN_FILES', True)
UTILS_EMAIL_DEBUG_PATH = getattr(settings, 'UTILS_EMAIL_DEBUG_PATH',
                                 os.path.join(settings.BASE_DIR, 'tmp', 'debug_email'))

GRAVATAR_DEFAULT_SIZE = getattr(settings, 'GRAVATAR_DEFAULT_SIZE', 50)
# 404, mm, identicon, monsterid, wavatar, retro, blank, http://mysite.com/default.jpg
GRAVATAR_DEFAULT_IMAGE = getattr(settings, 'GRAVATAR_DEFAULT_IMAGE', 'mm')
GRAVATAR_RATING = getattr(settings, 'GRAVATAR_RATING', 'g')  # g, pg, r, x
GRAVATAR_SECURE = getattr(settings, 'GRAVATAR_SECURE', False)

EMAIL_DOMAIN_BLACK_LIST = getattr(settings, 'EMAIL_DOMAIN_BLACK_LIST', (
    'mailinator.com', '10minutemail.com', 'spambog.com', 'tempinbox.com', 'mailmetrash.com',
    'tempemail.net', 'yopmail.com', 'sharklasers.com', 'guerrillamailblock.com', 'guerrillamail.com',
    'guerrillamail.net', 'guerrillamail.biz', 'guerrillamail.org', 'guerrillamail.de', 'spam4.me', 'spam.su',
    'inboxed.im', 'inboxed.pw', 'gomail.in', 'tokem.co', 'nomail.pw', 'yanet.me', 'powered.name', 'shut.ws',
    'vipmail.pw', 'powered.im', 'linuxmail.so', 'secmail.pw', 'shut.name', 'freemail.ms', 'mailforspam.com',
    'uroid.com', 'rmqkr.net',
))

SITE_DOMAIN = getattr(settings, 'SITE_DOMAIN', 'localhost')
DOMAIN_TITLE = getattr(settings, 'DOMAIN_TITLE', SITE_DOMAIN)

EMAIL_RETURN_PATH = getattr(settings, 'EMAIL_RETURN_PATH', None)
EMAIL_REPLY_TO = getattr(settings, 'EMAIL_REPLY_TO', None)

EMAIL_DEFAULT_CONTEXT = getattr(settings, 'EMAIL_DEFAULT_CONTEXT', 'dj_utils.context_processors.email_default')

LOG_DIR = getattr(settings, 'LOG_DIR', os.path.join(settings.BASE_DIR, 'logs'))
