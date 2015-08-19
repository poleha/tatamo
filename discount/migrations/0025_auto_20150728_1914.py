# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('discount', '0024_auto_20150727_1510'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='filtervalue',
            options={'ordering': ['title_int', 'title']},
        ),
        migrations.AddField(
            model_name='filtervalue',
            name='title_int',
            field=models.PositiveIntegerField(blank=True, default=0),
        ),
    ]
