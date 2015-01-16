# coding=utf-8
from __future__ import absolute_import
import os
import sys
from django.core.management.base import OutputWrapper
from django.core.management.commands.makemessages import check_programs, Command as DjangoMakemessagesCommand
from django.core.management.commands.compilemessages import Command as DjangoCompilemessagesCommand
from django.core.management.utils import handle_extensions


APPS = ('dj_utils',)
LANGUAGES = ('en', 'uk', 'ru', 'pl')

COMMANDS_LIST = ('makemessages', 'compilemessages')
COMMANDS_INFO = {
    'makemessages': 'make po-files',
    'compilemessages': 'compile po-files to mo-files',
}

GETTEXT_EXTENSIONS = {
    'django': ['html', 'txt'],
    'djangojs': ['js'],
}


class MakemessagesCommand(DjangoMakemessagesCommand):
    stdout = OutputWrapper(sys.stdout)
    verbosity = 1
    symlinks = False
    ignore_patterns = ['CVS', '.*', '*~', '*.pyc']
    no_obsolete = False
    keep_pot = False
    invoked_for_django = False
    locale_paths = []
    default_locale_path = None

    def _update_locale_paths(self, app_name):
        self.locale_paths = [os.path.join(app_name, 'locale').replace('\\', '/')]
        self.default_locale_path = self.locale_paths[0]
        if not os.path.exists(self.default_locale_path):
            os.makedirs(self.default_locale_path)

    @classmethod
    def get_command(cls, app_name, domain):
        assert domain in ('django', 'djangojs')
        check_programs('xgettext', 'msguniq', 'msgmerge', 'msgattrib')
        co = cls()
        co.domain = domain
        co.extensions = handle_extensions(GETTEXT_EXTENSIONS[domain])
        co._update_locale_paths(app_name)
        return co


class CompilemessagesCommand(DjangoCompilemessagesCommand):
    stdout = OutputWrapper(sys.stdout)
    verbosity = 1

    @classmethod
    def compilemessages(cls):
        check_programs('msgfmt')
        basedirs = [os.path.join(app, 'locale').replace('\\', '/') for app in APPS]
        co = cls()
        for basedir in basedirs:
            dirs = [os.path.join(basedir, locale, 'LC_MESSAGES').replace('\\', '/') for locale in LANGUAGES]
            locations = []
            for ldir in dirs:
                for dirpath, dirnames, filenames in os.walk(ldir):
                    locations.extend((dirpath, f) for f in filenames if f.endswith('.po'))
            if locations:
                co.compile_messages(locations)


def makemessages(*args):
    from django.conf import settings
    settings.configure()
    settings.MEDIA_ROOT = settings.STATIC_ROOT = '/-nopath-'
    check_programs('xgettext', 'msguniq', 'msgmerge', 'msgattrib')
    for app_name in APPS:
        for domain in ('django', 'djangojs'):
            co = MakemessagesCommand.get_command(app_name, domain)
            co.stdout.write("app: %s, domain: %s\n" % (app_name, domain))
            try:
                potfiles = co.build_potfiles()
                for locale in LANGUAGES:
                    if co.verbosity > 0:
                        co.stdout.write('processing locale %s\n' % locale)
                    for potfile in potfiles:
                        co.write_po_file(potfile, locale)
            finally:
                if not co.keep_pot:
                    co.remove_potfiles()


def compilemessages(*args):
    CompilemessagesCommand.compilemessages()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Available commands:'
        for c in COMMANDS_LIST:
            print c + ' - ' + COMMANDS_INFO[c]
    elif sys.argv[1] in COMMANDS_LIST:
        locals()[sys.argv[1]](*sys.argv[2:])
