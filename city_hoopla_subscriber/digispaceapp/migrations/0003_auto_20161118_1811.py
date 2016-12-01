# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('digispaceapp', '0002_auto_20161116_1753'),
    ]

    operations = [
        migrations.AddField(
            model_name='business',
            name='country_id',
            field=models.ForeignKey(blank=True, to='digispaceapp.Country', null=True),
        ),
        migrations.AddField(
            model_name='business',
            name='state_id',
            field=models.ForeignKey(blank=True, to='digispaceapp.State', null=True),
        ),
    ]
