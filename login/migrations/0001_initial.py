# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ExtendedUser',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('imageUrl', models.CharField(null=True, blank=True, max_length=512)),
                ('birthDay', models.DateField(null=True, blank=True)),
                ('gender', models.CharField(null=True, blank=True, max_length=1)),
                ('city', models.CharField(null=True, blank=True, max_length=512)),
                ('country', models.CharField(null=True, blank=True, max_length=512)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
