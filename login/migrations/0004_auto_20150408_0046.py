# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0003_auto_20150408_0037'),
    ]

    operations = [
        migrations.AlterField(
            model_name='extendeduser',
            name='birthDay',
            field=models.DateField(default='2002-01-01'),
            preserve_default=True,
        ),
    ]
