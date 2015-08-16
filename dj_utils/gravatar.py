import urllib
import hashlib
from . import settings as u_settings


def get_ava_url(email, size=None):
    if not size:
        size = u_settings.DJU_GRAVATAR_DEFAULT_SIZE
    return "%s://www.gravatar.com/avatar/%s?%s" % (
        (u_settings.DJU_GRAVATAR_SECURE and 'https' or 'http'),
        hashlib.md5(email.lower()).hexdigest(),
        urllib.urlencode({'d': u_settings.DJU_GRAVATAR_DEFAULT_IMAGE,
                          's': str(size),
                          'r': u_settings.DJU_GRAVATAR_RATING})
    )


def get_profile_url(email):
    return "%s://ru.gravatar.com/%s" % ((u_settings.DJU_GRAVATAR_SECURE and 'https' or 'http'),
                                        hashlib.md5(email.lower()).hexdigest())
