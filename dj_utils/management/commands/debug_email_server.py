# coding=utf-8
from __future__ import absolute_import
import sys
import os
import base64
import re
import datetime
import subprocess
from django.core.management.base import BaseCommand
from smtpd import SMTPServer
from dj_utils.settings import UTILS_EMAIL_DEBUG_PATH, UTILS_EMAIL_DEBUG_IN_CONSOLE, UTILS_EMAIL_DEBUG_IN_FILES


class DebuggingServer(SMTPServer):
    @staticmethod
    def _get_subject(data):
        subject_re = re.compile(r'^Subject: (.+)$', re.IGNORECASE)
        base64_re = re.compile(r'^=\?(.+)\?b\?(.+)\?=$', re.IGNORECASE)
        for line in data.split('\n'):
            m = subject_re.match(line)
            if m:
                subject = m.group(1).strip()
                m = base64_re.match(subject)
                if m:
                    charset, content = m.groups()
                    subject = unicode(base64.b64decode(content), 'utf8')
                return subject
        return ''

    @staticmethod
    def _get_fn(fn_base, n=None):
        if n is None:
            return os.path.join(UTILS_EMAIL_DEBUG_PATH, '{}.eml'.format(fn_base)).replace('\\', '/')
        else:
            return os.path.join(UTILS_EMAIL_DEBUG_PATH, '{}_{}.eml'.format(fn_base, n)).replace('\\', '/')

    def process_message(self, peer, mailfrom, rcpttos, data):
        try:
            if UTILS_EMAIL_DEBUG_IN_FILES:
                if not os.path.exists(UTILS_EMAIL_DEBUG_PATH):
                    os.makedirs(UTILS_EMAIL_DEBUG_PATH)
                fn_base = '%s_%s_%s_%s' % ('_'.join(rcpttos), self._get_subject(data), mailfrom,
                                          datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
                fn_base = re.sub(r'[:\*\?"<>\| ]+', '_', fn_base)
                fn = self._get_fn(fn_base)
                n = 1
                while os.path.exists(fn):
                    fn = self._get_fn(fn_base, n)
                    n += 1
                f = open(fn, 'w')
            inheaders = 1
            for line in data.split('\n'):
                if inheaders and not line:
                    if UTILS_EMAIL_DEBUG_IN_FILES:
                        f.write('X-Peer: %s\n' % peer[0])
                    if UTILS_EMAIL_DEBUG_IN_CONSOLE:
                        print 'X-Peer:', peer[0]
                    inheaders = 0
                if UTILS_EMAIL_DEBUG_IN_FILES:
                    f.write('%s\n' % line)
                if UTILS_EMAIL_DEBUG_IN_CONSOLE:
                    print line
        except Exception, e:
            print 'DebuggingServer error: %s' % e


class Command(BaseCommand):
    help = 'Run debug smtp server'

    def handle(self, *args, **options):
        subprocess.call([
            sys.executable,
            '-m', 'smtpd', '-n', '-c', 'dj_utils.management.commands.debug_email_server.DebuggingServer',
            'localhost:1025'
        ])
