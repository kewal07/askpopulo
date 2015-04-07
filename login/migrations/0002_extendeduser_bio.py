# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='extendeduser',
            name='bio',
            field=models.CharField(blank=True, max_length=1024, null=True),
            preserve_default=True,
        ),
    ]
