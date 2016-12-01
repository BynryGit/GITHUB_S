# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('digispaceapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='advert',
            name='discount_end_date',
            field=models.CharField(default=None, max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='advert',
            name='discount_start_date',
            field=models.CharField(default=None, max_length=50, null=True, blank=True),
        ),
    ]
