from django.conf import settings
from django.core.management import BaseCommand, CommandError
from django.db import DEFAULT_DB_ALIAS, connections
from django.apps.registry import apps as project_apps


def get_apps_list(apps, external_apps):
    r = set()
    all_apps_names = project_apps.app_configs.keys()
    if apps:
        for app in apps:
            if app not in all_apps_names:
                raise CommandError('App "{}" is not exists.'.format(app))
            r.add(app)
    else:
        for app_name, app_config in project_apps.app_configs.items():
            if app_config.path.startswith(settings.BASE_DIR):
                r.add(app_name)
    if external_apps:
        for app_name, app_config in project_apps.app_configs.items():
            if not app_config.path.startswith(settings.BASE_DIR):
                r.add(app_name)
    return list(r)


class Command(BaseCommand):
    help = 'Prints the drop ALL index and foreign key statements for tables from apps.'

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument('--database',  action='store', dest='database', default=DEFAULT_DB_ALIAS,
                            help='Database that will be used. Defaults to the "default" database.')
        parser.add_argument('--application', '-a', action='append', dest='apps', default=[], metavar='APPNAME',
                            help='The application name. If not set then using all project app (without external apps).')
        parser.add_argument('--external-apps', action='store_true', dest='external_apps',
                            help='Include all external applications in the project.')
        parser.add_argument('--info', '-i', action='store_true', dest='info',
                            help='Prints comments about application name and model name.')

    @classmethod
    def _get_fks(cls, conn, table):
        r = []
        for key, info in conn.introspection.get_constraints(conn.cursor(), table).iteritems():
            if info['foreign_key'] and not info['primary_key']:
                r.append(key)
        return r

    @classmethod
    def _get_indexes(cls, conn, table):
        r = []
        for key, info in conn.introspection.get_constraints(conn.cursor(), table).iteritems():
            if info['index'] and not info['foreign_key'] and not info['primary_key']:
                r.append(key)
        return r

    @classmethod
    def _sql_drop_fk(cls, conn, table, keys):
        qn = conn.ops.quote_name
        r = []
        for key in keys:
            r.append("ALTER TABLE {table} DROP FOREIGN KEY {key};".format(
                table=qn(table), key=qn(key)
            ))
        return r

    @classmethod
    def _sql_drop_index(cls, conn, table, indexes):
        qn = conn.ops.quote_name
        r = []
        for index in indexes:
            r.append("DROP INDEX {index} ON {table};".format(
                table=qn(table), index=qn(index)
            ))
        return r

    def handle(self, *args, **options):
        apps = get_apps_list(options['apps'], options['external_apps'])
        info = options['info']
        connection = connections[options['database']]
        if connection.vendor != 'mysql':
            raise CommandError('This command does not support "{}" DB backend. Only mysql.'.format(connection.vendor))
        for app in apps:
            app_config = project_apps.app_configs[app]
            if info:
                print '+Application: {}'.format(app)
            for model_name, model in app_config.models.iteritems():
                if model._meta.proxy:
                    continue
                if info:
                    print '-Model: {}'.format(model_name)
                db_table = model._meta.db_table
                if info:
                    print '>Table: {}'.format(db_table)

                fks = self._get_fks(connection, db_table)
                if fks:
                    print '\n'.join(self._sql_drop_fk(connection, db_table, fks))
                else:
                    if info:
                        print '..there are not foreign keys..'

                ixs = self._get_indexes(connection, db_table)
                if ixs:
                    print '\n'.join(self._sql_drop_index(connection, db_table, ixs))
                else:
                    if info:
                        print '..there are not indexes..'

                if info:
                    print
            if info:
                print
