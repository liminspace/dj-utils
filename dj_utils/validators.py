# coding=utf-8
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy, ugettext as _
from . import settings as u_settings


def validate_email_domain(email):
    """ Валідація email по чорному списку доменів. """
    try:
        domain = email.split('@', 1)[1]
    except IndexError:
        pass
    else:
        if domain.lower() in u_settings.DJU_EMAIL_DOMAIN_BLACK_LIST:
            raise ValidationError(_(u'Email with domain "%s" is disallowed.') % domain)


validate_phone_number12 = RegexValidator(  # Валідація номеру телефону в форматі +XX XXX XXXXXXX.
    r'^\+[\d]{12}$',
    ugettext_lazy('Phone number must be in +XX XXX XXXXXXX format.'),
    'invalid'
)
