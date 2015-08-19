# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import multi_image_upload.models
from django.utils.timezone import utc
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('discount', '0008_auto_20150705_1339'),
    ]

    operations = [
        migrations.AddField(
            model_name='productchanger',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2015, 7, 5, 12, 1, 52, 576457, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='productchanger',
            name='edited',
            field=models.DateTimeField(auto_now=True, default=datetime.datetime(2015, 7, 5, 12, 2, 1, 463912, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='productchanger',
            name='title',
            field=models.CharField(verbose_name='Название', default='', blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name='productchanger',
            name='user',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='productchangerimage',
            name='image',
            field=multi_image_upload.models.MyImageField(verbose_name='Изображение', upload_to='discount_product', db_index=True),
        ),
    ]
