# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0005_auto_20150417_1255'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vote',
            name='choice',
            field=models.ForeignKey(to='polls.Choice'),
        ),
    ]
