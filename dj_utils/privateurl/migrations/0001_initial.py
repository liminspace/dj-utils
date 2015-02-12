# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import dj_utils.fields.json
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PrivateUrl',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('action', models.SlugField(max_length=24, verbose_name='action')),
                ('token', models.SlugField(max_length=64, verbose_name='token')),
                ('expire', models.DateTimeField(db_index=True, null=True, verbose_name='expire', blank=True)),
                ('data', dj_utils.fields.json.JSONField(default=None, verbose_name='data', blank=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created', db_index=True)),
                ('used_limit', models.PositiveIntegerField(default=1, help_text='Set 0 to unlimit.', verbose_name='used limit')),
                ('used_counter', models.PositiveIntegerField(default=0, verbose_name='used counter')),
                ('first_used', models.DateTimeField(null=True, verbose_name='first used', blank=True)),
                ('last_used', models.DateTimeField(null=True, verbose_name='last used', blank=True)),
                ('auto_delete', models.BooleanField(default=False, help_text='Delete object if it can no longer be used.', db_index=True, verbose_name='auto delete')),
                ('user', models.ForeignKey(verbose_name='user', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-created',),
                'db_table': 'dju_privateurl',
                'verbose_name': 'private url',
                'verbose_name_plural': 'privete urls',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='privateurl',
            unique_together=set([('action', 'token')]),
        ),
    ]
