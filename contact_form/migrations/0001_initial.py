# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactForm',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=256, verbose_name='Ваше имя')),
                ('email', models.EmailField(max_length=254, verbose_name='E-MAIL')),
                ('phone', models.CharField(blank=True, max_length=256, verbose_name='Телефон', null=True)),
                ('body', models.TextField(verbose_name='Сообщение')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('created', 'created'), ('checked', 'checked')], max_length=10, default='created')),
                ('user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['created'],
            },
        ),
    ]
