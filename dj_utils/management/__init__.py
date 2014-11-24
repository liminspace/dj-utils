# coding=utf-8
from __future__ import absolute_import
import datetime
import inspect
import os
from django.core.management import BaseCommand
from dj_utils import settings as u_settings


class LoggingBaseCommand(BaseCommand):
    log_fn = None
    log_dir = u_settings.LOG_DIR

    def log(self, msg, add_time=True, stdout=True, double_br=False):
        f = open(os.path.join(self.log_dir, self.get_log_fn()), 'a')
        msg += '\n' * (int(bool(double_br)) + 1)
        if add_time:
            msg = u'[%s] %s' % (datetime.datetime.now().strftime(u'%d.%m.%Y %H:%M:%S'), msg)
        if stdout:
            self.stdout.write(msg)
        f.write(msg.encode('utf8'))

    def get_log_fn(self):
        if self.log_fn is None:
            return '%s.log' % os.path.splitext(os.path.basename(inspect.getfile(self.__class__)))[0]
        return self.log_fn
