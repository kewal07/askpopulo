# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0003_auto_20150401_1809'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='expiry',
            field=models.DateTimeField(blank=True, null=True),
            preserve_default=True,
        ),
    ]
