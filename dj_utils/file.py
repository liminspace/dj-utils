# coding=utf-8
from __future__ import absolute_import
import os
from StringIO import StringIO
from django.core.files.uploadedfile import InMemoryUploadedFile


def truncate_file(f):
    """
    Очищає завантажений файл і дозволяє в нього записувати свій файл. (Не призначено для дуже об'ємних файлів!)
    Також може очищати звичайний відкритий файл.
    Приклад:
        truncate_file(request.FILES['file'])

        with open('/tmp/file', 'rb+') as f:
            truncate_file(f)
    """
    if isinstance(f, InMemoryUploadedFile):
        f.file = StringIO()
    else:
        f.seek(0)
        f.truncate(0)


def makedirs_for_filepath(filepath, mode=0o777):
    """
    Створює папки для файлу filepath, якщо ці папки не існують.
    """
    dirname = os.path.dirname(filepath)
    if not os.path.exists(dirname):
        os.makedirs(dirname, mode=mode)
