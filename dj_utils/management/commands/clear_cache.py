from django.core.management import BaseCommand
from django.core.cache import cache


class Command(BaseCommand):
    help = 'Clear cache.'

    def handle(self, *args, **options):
        print 'Clear cache...'
        cache.clear()
        print 'OK'
