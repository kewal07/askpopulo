# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0002_extendeduser_bio'),
    ]

    operations = [
        migrations.AddField(
            model_name='extendeduser',
            name='profession',
            field=models.CharField(null=True, blank=True, max_length=512),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='extendeduser',
            name='state',
            field=models.CharField(null=True, blank=True, max_length=512),
            preserve_default=True,
        ),
    ]
