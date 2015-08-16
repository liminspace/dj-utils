from django.contrib.sites.models import Site
from .http import full_url


def email_default(request=None):
    """
    Default context for render email templates.
    """
    return {
        'SITE': lambda: Site.objects.get_current(),
        'HOMEPAGE_URL': full_url,
    }
