# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('discount', '0010_userprofile_role'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdminMonitorMail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('keys', models.TextField(blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name='productbanner',
            name='hashed',
            field=models.CharField(blank=True, max_length=40),
        ),
        migrations.AddField(
            model_name='productchanger',
            name='hashed',
            field=models.CharField(blank=True, max_length=40),
        ),
        migrations.AlterField(
            model_name='product',
            name='title',
            field=models.CharField(verbose_name='Название', default='', max_length=500),
        ),
    ]
