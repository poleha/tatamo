# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contact_form', '0002_remove_contactform_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='contactform',
            name='status',
            field=models.IntegerField(choices=[(1, 'created'), (2, 'checked')], default=1),
        ),
    ]
