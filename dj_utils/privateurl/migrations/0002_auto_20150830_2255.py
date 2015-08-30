# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('privateurl', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='privateurl',
            name='action',
            field=models.SlugField(max_length=32, verbose_name='action'),
        ),
    ]
