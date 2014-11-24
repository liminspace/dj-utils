# coding=utf-8
from __future__ import absolute_import
from dj_utils import cyclictask_core
from dj_utils.management import LoggingBaseCommand


class Command(LoggingBaseCommand):
    args = '<pid file path>'
    help = 'Run cyclic tasks.'

    def handle(self, *args, **options):
        try:
            pid_fn = args[0]
        except IndexError:
            pid_fn = None
        cyclictask_core.init(pid_fn=pid_fn)
