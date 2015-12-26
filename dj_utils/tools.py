import time
import datetime
import pytz
from django.utils import timezone


def int2base36(n):
    """
    Convert int base10 to base36.
    Back convert: int('<base36>', 36)
    """
    assert isinstance(n, (int, long))
    c = '0123456789abcdefghijklmnopqrstuvwxyz'
    if n < 0:
        return '-' + int2base36(-n)
    elif n < 36:
        return c[n]
    b36 = ''
    while n != 0:
        n, i = divmod(n, 36)
        b36 = c[i] + b36
    return b36


def datetime_to_dtstr(dt=None):
    """
    Comvert datetime to short text.
    If datetime has timezone then it will be convert to UTC0.
    """
    if dt is None:
        dt = datetime.datetime.utcnow()
    elif timezone.is_aware(dt):
        dt = dt.astimezone(tz=pytz.UTC)
    return int2base36(int(time.mktime(dt.timetuple()) * 1e3 + dt.microsecond / 1e3))


def dtstr_to_datetime(dtstr, to_tz=None, fail_silently=True):
    """
    Convert result from datetime_to_dtstr to datetime in timezone UTC0.
    """
    try:
        dt = datetime.datetime.utcfromtimestamp(int(dtstr, 36) / 1e3)
        if to_tz:
            dt = timezone.make_aware(dt, timezone=pytz.UTC)
            if to_tz != pytz.UTC:
                dt = dt.astimezone(to_tz)
        return dt
    except ValueError, e:
        if not fail_silently:
            raise e
        return None
