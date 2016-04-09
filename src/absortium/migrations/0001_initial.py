# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-07 19:20
from __future__ import unicode_literals

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Offer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.IntegerField(choices=[('sell', 1), ('buy', 2)])),
                ('pair', models.IntegerField(choices=[('BTC_ETH', 1), ('BTC_XMR', 2)])),
                ('amount', models.FloatField(validators=[django.core.validators.MinValueValidator(0.001)])),
                ('price', models.FloatField(validators=[django.core.validators.MinValueValidator(0.001)])),
            ],
            options={
                'ordering': ('price',),
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.IntegerField(choices=[('sell', 1), ('buy', 2)])),
                ('pair', models.IntegerField(choices=[('BTC_ETH', 1), ('BTC_XMR', 2)])),
                ('amount', models.FloatField(validators=[django.core.validators.MinValueValidator(0.001)])),
                ('price', models.FloatField(validators=[django.core.validators.MinValueValidator(0.001)])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('price',),
            },
        ),
    ]
