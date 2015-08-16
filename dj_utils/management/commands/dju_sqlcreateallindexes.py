from django.core.management import BaseCommand, CommandError
from django.db import DEFAULT_DB_ALIAS, connections
from django.apps.registry import apps as project_apps
from .dju_sqldropallindexes import get_apps_list


class Command(BaseCommand):
    help = 'Prints the create ALL index and foreign key statements for tables from apps.'

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
    def _get_unique_index_fields(cls, model):
        unique_ix_fields = []
        for f in model._meta.local_fields:
            if f.primary_key:
                continue
            elif f.unique:
                unique_ix_fields.append([f])
        for ut in model._meta.unique_together:
            unique_ix_fields.append([model._meta.get_field(f)[0] for f in ut])
        return unique_ix_fields

    def handle(self, *args, **options):
        apps = get_apps_list(options['apps'], options['external_apps'])
        info = options['info']
        connection = connections[options['database']]
        if connection.vendor != 'mysql':
            raise CommandError('This command does not support "{}" DB backend. Only mysql.'.format(connection.vendor))
        se = connection.schema_editor()
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

                ix_sql = se._model_indexes_sql(model)
                if ix_sql:
                    print '\n'.join('{};'.format(sql) for sql in ix_sql)
                else:
                    if info:
                        print '..there are not indexes..'

                unique_ix_sql = []
                for fields in self._get_unique_index_fields(model):
                    unique_ix_sql.append(se._create_unique_sql(model, [f.column for f in fields]))
                if unique_ix_sql:
                    print '\n'.join('{};'.format(sql) for sql in unique_ix_sql)
                else:
                    if info:
                        print '..there are not unique indexes..'

                fk_sql = []
                for f in model._meta.local_fields:
                    if f.rel and f.db_constraint:
                        fk_sql.append(se._create_fk_sql(
                            model, f, "_fk_%(to_table)s_%(to_column)s"
                        ))

                if fk_sql:
                    print '\n'.join('{};'.format(sql) for sql in fk_sql)
                else:
                    if info:
                        print '..there are not foreign keys..'

                if info:
                    print
            if info:
                print
