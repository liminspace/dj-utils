# coding=utf-8
from __future__ import absolute_import
import os
import re
import datetime
from django.conf import settings
from django.utils.crypto import get_random_string
from dj_utils.tools import datetime_to_dtstr, dtstr_to_datetime


TMP_PREFIX = '__tmp__'


def generate_filename(ext=None, label=None):
    """
    Генерує ім'я фалу.
    """
    if ext and not ext.startswith('.'):
        ext = '.' + ext
    if label:
        label = re.sub(r'[^a-z0-9_\-]', '', label, flags=re.I)[:60]
    return '{dtstr}_{rand}{label}{ext}'.format(
        dtstr=datetime_to_dtstr(),
        rand=get_random_string(4, 'abcdefghijklmnopqrstuvwxyz0123456789'),
        label='_' + label if label else '',
        ext=ext or '',
    )


def add_tmp_prefix_to_filename(filename):
    """ Додає префікс тимчасового файлу до імені файлу """
    return TMP_PREFIX + filename


def add_ending_to_filename(filename, ending):
    """ Додає закінчення до імені файлу """
    ending = re.sub(r'[^a-z0-9_\-]', '', ending, flags=re.I)[:60]
    if ending:
        fn, ext = os.path.splitext(filename)
        filename = '{fn}_{ending}{ext}'.format(fn=fn, ending=ending, ext=ext)
    return filename


def get_subdir_for_filename(filename):
    """ Повертає назву підпапки для файлу (dtstr[-2:]) """
    if filename.startswith(TMP_PREFIX):
        filename = filename[len(TMP_PREFIX):]
    m = re.match(r'^([a-z0-9]+?)_.+', filename)
    if m:
        return m.group(1)[-2:]
    return 'other'


def url_to_fn(url):
    """
    Повертає шлях до файлу MEDIA по URL-адресі
    """
    if url.startswith(settings.MEDIA_URL):
        url = url[len(settings.MEDIA_URL):]
    fn = os.path.join(settings.MEDIA_ROOT, os.path.normpath(url)).replace('\\', '/')
    return fn


def remove_file_by_url(url):
    """
    Видаляє файл по URL, якщо він знаходиться в папці MEDIA.
    """
    fn = url_to_fn(url)
    if os.path.exists(fn) and os.path.isfile(fn):
        os.remove(fn)


def move_to_permalink(url):
    r = re.compile(r'^(.+?)(%s)(.+?)$' % TMP_PREFIX, re.I)
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
        path = os.path.join(settings.MEDIA_ROOT, subdir).replace('\\', '/')
        old_dt = datetime.datetime.utcnow() - datetime.timedelta(hours=max_lifetime)
        r = re.compile(r"^(%s)([a-z0-9_\-]+?)((?:_.+?)?)(\.[a-z]{3,4})$" % tmp_prefix, re.I)
        for fn in os.listdir(path):
            m = r.match(fn)
            if m:
                prefix, name, label, ext = m.groups()
                fdt = dtstr_to_datetime(name)
                if fdt and old_dt > fdt:
                    os.remove(os.path.join(path, fn).replace('\\', '/'))
