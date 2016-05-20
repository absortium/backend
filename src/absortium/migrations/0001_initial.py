# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-15 10:34
from __future__ import unicode_literals

from decimal import Decimal

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
            name='Account',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=8, default=0, max_digits=22)),
                ('address', models.CharField(max_length=50)),
                ('currency', models.IntegerField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='accounts',
                                            to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Deposit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('amount', models.DecimalField(decimal_places=8, max_digits=15)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='deposits',
                                              to='absortium.Account')),
            ],
        ),
        migrations.CreateModel(
            name='Exchange',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField()),
                ('amount', models.DecimalField(decimal_places=8, max_digits=15)),
                ('price', models.DecimalField(decimal_places=8, max_digits=15)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('from_currency', models.IntegerField()),
                ('to_currency', models.IntegerField()),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exchanges',
                                            to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-price', 'created'],
            },
        ),
        migrations.CreateModel(
            name='Offer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_currency', models.IntegerField()),
                ('to_currency', models.IntegerField()),
                ('amount', models.DecimalField(decimal_places=8, default=Decimal('0.0'), max_digits=22)),
                ('price', models.DecimalField(decimal_places=8, max_digits=15)),
            ],
            options={
                'ordering': ('price',),
            },
        ),
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=8, max_digits=15)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tests',
                                            to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Withdrawal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('amount', models.DecimalField(decimal_places=8, max_digits=15)),
                ('address', models.CharField(max_length=50)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='withdrawals',
                                              to='absortium.Account')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='offer',
            unique_together=set([('to_currency', 'from_currency', 'price')]),
        ),
        migrations.AlterUniqueTogether(
            name='account',
            unique_together=set([('currency', 'owner')]),
        ),
    ]