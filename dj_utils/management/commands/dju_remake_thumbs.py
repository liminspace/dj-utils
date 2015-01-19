# coding=utf-8
from __future__ import absolute_import
from django.conf import settings
from dj_utils.management import LoggingBaseCommand
from dj_utils.upload import remake_thumbs


class Command(LoggingBaseCommand):
    help = 'Remove and remake thumbs for images.'

    def handle(self, *args, **options):
        profiles = settings.DJU_IMG_UPLOAD_PROFILES.keys()
        if profiles:
            self.log('Start')
            removed, created = remake_thumbs(profiles)
            self.log('End. Removed / created thumbs: {rm} / {cr}'.format(rm=removed, cr=created), double_br=True)
        else:
            self.log("The project doesn't have profiles in DJU_IMG_UPLOAD_PROFILESd.")
