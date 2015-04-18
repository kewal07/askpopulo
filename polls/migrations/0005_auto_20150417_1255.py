# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0004_question_expiry'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vote',
            name='choice',
            field=models.OneToOneField(to='polls.Choice'),
        ),
    ]
