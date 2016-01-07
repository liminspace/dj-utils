# coding=utf-8
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy


validate_phone_number12 = RegexValidator(  # Валідація номеру телефону в форматі +XX XXX XXXXXXX.
    r'^\+[\d]{12}$',
    ugettext_lazy('Phone number must be in +XX XXX XXXXXXX format.'),
    'invalid'
)
