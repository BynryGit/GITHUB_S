# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('digispaceapp', '0003_auto_20160928_1022'),
    ]

    operations = [
        migrations.AddField(
            model_name='consumerprofile',
            name='city_place_id',
            field=models.ForeignKey(blank=True, to='digispaceapp.City_Place', null=True),
        ),
    ]
