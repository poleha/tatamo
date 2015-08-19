# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import multi_image_upload.models


class Migration(migrations.Migration):

    dependencies = [
        ('discount', '0006_auto_20150702_1644'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='body',
            field=models.TextField(blank=True, verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='productchangerimage',
            name='image',
            field=multi_image_upload.models.MyImageField(upload_to='discount_product_changer', verbose_name='Изображение', db_index=True),
        ),
    ]
