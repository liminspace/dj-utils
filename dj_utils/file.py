# coding=utf-8
from StringIO import StringIO
from django.core.files.uploadedfile import InMemoryUploadedFile


def truncate_file(f):  # todo remove! use dju-common
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
