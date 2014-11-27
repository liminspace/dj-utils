# coding=utf-8
from __future__ import absolute_import
from django.db import connection
from django.utils.log import getLogger


logger = getLogger(__name__)


class QueryCountDebugMiddleware(object):
    """
    Логує кількість та час запитів в БД для відповідей з кодом 200.

    Для підключення треба в settings додати:
    ...
    if DEBUG:
        MIDDLEWARE_CLASSES = ('dj_utils.middleware.QueryCountDebugMiddleware',) + MIDDLEWARE_CLASSES
    ...
    LOGGING = {
        ...
        'loggers': {
            ...
            'dj_utils.middleware': {
                'handlers': ['console'],
                'level': 'DEBUG',
            },
            ...
        },
        ...
    }
    """
    def process_response(self, request, response):
        if response.status_code == 200:
            total_time = 0
            for query in connection.queries:
                query_time = query.get('time')
                if query_time is None:
                    # django-debug-toolbar манкіпатчить connection cursor wrapper і
                    # додає додаткову інформацію до елементів connection.queries.
                    # Час запитів зберігається під ключем 'duration' замість 'time' і
                    # задається в мілісекундах, а не секундах.
                    query_time = query.get('duration', 0) / 1000.
                total_time += float(query_time)
            logger.debug('SQL queries count: %s, total time: %s s' % (len(connection.queries), total_time))
        return response
