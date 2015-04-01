# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0002_question_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='description',
            field=models.CharField(blank=True, max_length=400, null=True),
            preserve_default=True,
        ),
    ]
