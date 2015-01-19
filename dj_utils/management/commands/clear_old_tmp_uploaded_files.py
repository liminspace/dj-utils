# coding=utf-8
from __future__ import absolute_import
from optparse import make_option
from django.core.management import CommandError, BaseCommand
from dj_utils.management import LoggingBaseCommand
from dj_utils.upload import remove_old_tmp_files


class Command(LoggingBaseCommand):
    help = 'Remove old temporary uploaded files.'
    option_list = (
        make_option('-d', '--dir', action='append', dest='dirs', default=[],
                    help='Path to directory with files which need to clean.'),
        make_option('-m', '--max-lifetime', action='store', type='int', dest='max_lifetime', default=168,
                    help='Time of life file in hours. Default: 168 (7 days)'),
        make_option('-r', '--recursive', action='store_true', dest='recursive', default=False,
                    help='Using recursive scan.'),
    ) + BaseCommand.option_list

    def handle(self, *args, **options):
        if not options['dirs']:
            raise CommandError('Please, specify path to dir using option -d or --dir: -d /path/to/dir')
        self.log('Start')
        self.log('Dirs: {}'.format(', '.join(options['dirs'])), add_time=False)
        self.log('Max lifetime: {} h'.format(options['max_lifetime']), add_time=False)
        self.log('Recursive: {}'.format(('no', 'yes')[options['recursive']]), add_time=False)
        removed, total = remove_old_tmp_files(options['dirs'], max_lifetime=options['max_lifetime'],
                                              recursive=options['recursive'])
        self.log('End. Removed: {rm} / {tt}'.format(rm=removed, tt=total), double_br=True)
