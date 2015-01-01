# coding=utf-8
from __future__ import absolute_import
import traceback
from django.conf import settings
from dj_utils.mail import RenderMailSender
from dj_utils.management import LoggingBaseCommand


class Command(LoggingBaseCommand):
    help = 'Send the test email.'
    args = '<emails>'

    def handle(self, *args, **options):
        if not args:
            self.log('Please, pass the email list as args: '
                     'manage.py send_test_email mail1@domain.com email2@domain.com ...', add_time=False)
            return
        m = RenderMailSender('dj_utils/mail/test.html', lang=settings.LANGUAGE_CODE)
        for email in set(args):
            self.log('Send the test email to {email}... '.format(email=email), ending='')
            try:
                m.send(email)
                self.log('OK', add_time=False)
                end_with_error = False
            except Exception, e:
                self.log('FAIL', add_time=False)
                self.log(traceback.format_exc(), add_time=False)
                end_with_error = True
                raise e
            finally:
                if end_with_error:
                    self.log('End with error', stdout=False)
        self.log('Done')
