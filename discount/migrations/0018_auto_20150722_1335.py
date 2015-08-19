# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('discount', '0017_productchangercondition_created'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='link',
            field=models.CharField(blank=True, max_length=4000),
        ),
        migrations.AddField(
            model_name='productchanger',
            name='link',
            field=models.CharField(blank=True, max_length=4000),
        ),
    ]
