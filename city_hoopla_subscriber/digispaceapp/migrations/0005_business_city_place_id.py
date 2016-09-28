# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('digispaceapp', '0004_consumerprofile_city_place_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='business',
            name='city_place_id',
            field=models.ForeignKey(blank=True, to='digispaceapp.City_Place', null=True),
        ),
    ]
