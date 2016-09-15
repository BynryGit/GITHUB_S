# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('digispaceapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('Item_video_id', models.AutoField(serialize=False, editable=False, primary_key=True)),
                ('Item_video_name', models.FileField(max_length=500, null=True, upload_to=b'images/user_images/', blank=True)),
                ('creation_date', models.DateTimeField(null=True, blank=True)),
                ('created_by', models.CharField(max_length=500, null=True, blank=True)),
                ('updated_by', models.CharField(max_length=500, null=True, blank=True)),
                ('updation_date', models.DateTimeField(null=True, blank=True)),
            ],
        ),
    ]
