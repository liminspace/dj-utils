# coding=utf-8
from __future__ import absolute_import
import os
import re
import time
import datetime
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from dj_utils import settings as u_settings


def natural_sorted(iterable, cmp_func=None, reverse=False):
    reg = re.compile(r'([0-9]+)')
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in reg.split(key)]
    return sorted(iterable, key=alphanum_key, cmp=cmp_func, reverse=reverse)


def int2base36(n):
    """
    Конвертує ціле число n в 36-ткову систему числення.
    Зворотня конвертація робиться так: int('<число в 36-тковій системі числення>', 36)
    """
    assert isinstance(n, (int, long))
    c = '0123456789abcdefghijklmnopqrstuvwxyz'
    sign = ''
    if n < 0:
        sign, n = '-', -n
    if 0 <= n < 36:
        return sign + c[n]
    b36 = ''
    while n != 0:
        n, i = divmod(n, 36)
        b36 = c[i] + b36
    return sign + b36


def datetime_to_dtstr(dt=None):
    """
    Конвертує датучас в короткий текст.
    Якщо передається дата в якомусь часовому поясі, то він конвертується на UTC0.
    """
    if dt is None:
        dt = datetime.datetime.utcnow()
    else:
        dt = dt.replace(tzinfo=None)
    return int2base36(int(time.mktime(dt.timetuple()) * 1e3 + dt.microsecond / 1e3))


def dtstr_to_datetime(dtstr):
    """
    Конвертує результат datetime_to_dtstr в датучас в часовому поясі UTC0.
    """
    try:
        return datetime.datetime.fromtimestamp(int(dtstr, 36) / 1e3)
    except ValueError:
        return None


def load_object_by_name(obj_name):
    """
    Імпортує та повертає об'єкт з пакету по назві.
    Приклад використання:
        MyForm = load_object_by_name('myapp.forms.MyAnyForm')
    """
    parts = obj_name.split('.')
    t = __import__('.'.join(parts[:-1]), fromlist=(parts[-1],))
    return getattr(t, parts[-1])

    
def parse_datetime_aware(s, tz=None):
    """
    Парсить текст з датою в абсолютну дату (aware).
    """
    assert settings.USE_TZ
    if isinstance(s, datetime.datetime):
        return s
    d = parse_datetime(s)
    if d is None:
        raise ValueError
    return timezone.make_aware(d, tz or timezone.get_current_timezone())


def long_number_readable(value):
    """
    Convert big integer (>=999) to readable form.
    1000 => 1k.
    2333 => 2.3k.
    1000000 => 1 mln.
    1258000 => 1.26 mln.
    """
    assert isinstance(value, (int, long))
    if value < 1000:
        return value
    formats = (
        (10 ** 6, 10 ** 3, u'%d', u'%.1f', _('k.')),
        (10 ** 9, 10 ** 6, u'%d', u'%.2f', _(' mln.')),
        (10 ** 12, 10 ** 9, u'%d', u'%.3f', _(' bln.')),
    )
    for m, d, inf, fnf, n in formats:
        if value < m:
            return ((inf if value % d == 0 else fnf) + n) % (value / float(d))
    return value


def log_to_file(msg, double_br=False, add_time=True, fn=None):
    fn = fn or os.path.join(settings.LOG_DIR, 'log.log').replace('\\', '/')
    with open(fn, 'a') as f:
        msg += '\n' * (int(bool(double_br)) + 1)
        if add_time:
            msg = u'[%s] %s' % (datetime.datetime.now().strftime(u'%d.%m.%Y %H:%M:%S'), msg)
        f.write(msg.encode('utf8'))


def log_memory_usage(desc='test'):
    try:
        import psutil
    except ImportError:
        raise ImportError("Can't import psutil. Please, install psutil (pip intall psutil).")
    proc = psutil.Process(os.getpid())
    mem = proc.get_memory_info()[0] / float(2 ** 20)
    log_to_file('%s: %s MB\n' % (desc, mem), add_time=False,
                fn=os.path.join(u_settings.LOG_DIR, 'memory_usage.log').replace('\\', '/'))
