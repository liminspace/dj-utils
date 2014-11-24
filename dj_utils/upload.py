# coding=utf-8
from __future__ import absolute_import
import StringIO
import os
import re
import datetime
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from dj_utils.tools import datetime_to_dtstr, dtstr_to_datetime


TMP_PREFIX = '__tmp_'


def generate_filename(ext, label=None, tmp=True):
    """
    Генерує ім'я фалу.
    Якщо tmp=True, тоді до імені файлу буде додано префікс, який вказуватиме, що файл тимчасовий.
    """
    return '%s%s%s.%s' % (
        TMP_PREFIX if tmp else '',
        datetime_to_dtstr(),
        '_' + label if label else '',
        ext
    )


def truncate_uploaded_file(uploaded_file):
    """
    Очищає завантажений файл і дозволяє в нього записувати свій файл.
    Не призначено для дуже об'ємних файлів!
    """
    if isinstance(uploaded_file, InMemoryUploadedFile):
        uploaded_file.file = StringIO.StringIO()
    else:
        uploaded_file.file.seek(0)
        uploaded_file.file.truncate(0)
    uploaded_file.file.seek(0)


def url_to_fn(url):
    """
    Повертає шлях до файлу MEDIA по URL-адресі
    """
    if url.startswith(settings.MEDIA_URL):
        url = url[len(settings.MEDIA_URL):]
    fn = os.path.join(settings.MEDIA_ROOT, os.path.normpath(url))
    return fn


def remove_file_by_url(url):
    """
    Видаляє файл по URL, якщо він знаходиться в папці MEDIA.
    """
    fn = url_to_fn(url)
    if os.path.exists(fn) and os.path.isfile(fn):
        os.remove(fn)


def move_to_permalink(url):
    r = re.compile(r'^(.+?)(%s)(.+?)$' % TMP_PREFIX, re.IGNORECASE)
    url_m = r.match(url)
    if url_m:
        fn = url_to_fn(url)
        if os.path.exists(fn) and os.path.isfile(fn):
            fn_m = r.match(fn)
            if fn_m:
                os.rename(fn, fn_m.group(1) + url_m.group(3))
                url = url_m.group(1) + url_m.group(3)
    return url


def remove_old_tmp_files(subdirs, max_lifetime=(7 * 24), tmp_prefix=TMP_PREFIX):
    """
    Видалення старих тимчасових файлів.
    Запускати функцію періодично раз на добу або рідше.
    max_lifetime -- час життя файлу, в годинах.
    Запуск в консолі:
    # python manage.py shell
    > from dj_utils.upload import remove_old_tmp_files
    > remove_old_tmp_files(['images'], (4 * 24))
    """
    for subdir in subdirs:
        path = os.path.join(settings.MEDIA_ROOT, subdir)
        old_dt = datetime.datetime.utcnow() - datetime.timedelta(hours=max_lifetime)
        r = re.compile(r"^(%s)([a-z0-9_\-]+?)((?:_.+?)?)(\.[a-z]{3,4})$" % tmp_prefix, re.IGNORECASE)
        for fn in os.listdir(path):
            m = r.match(fn)
            if m:
                prefix, name, label, ext = m.groups()
                fdt = dtstr_to_datetime(name)
                if fdt and old_dt > fdt:
                    os.remove(os.path.join(path, fn))
