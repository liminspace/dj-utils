# coding=utf-8
from __future__ import absolute_import
from django.conf import settings


def mt_fields(*fields):
    """
    Повертає список полів для мультимовних полів моделей.
    Приклад:
        print mt_fields('name', 'desc)
        ['name', 'name_en', 'name_uk', 'desc', 'desc_en', 'desc_uk']

        MyModel.objects.only(*mt_fields('name', 'desc', 'content'))
    """
    langs = map(lambda t: t[0], settings.LANGUAGES)
    fl = []
    for field in fields:
        fl.append(field)
        for lang in langs:
            fl.append('{}_{}'.format(field, lang))
    return fl
