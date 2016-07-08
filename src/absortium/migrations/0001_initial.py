# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-07-07 20:44
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


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
                ('amount', models.DecimalField(decimal_places=8, default=0, max_digits=26)),
                ('address', models.CharField(max_length=50)),
                ('currency', models.CharField(max_length=4)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('owner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='accounts', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-created',),
            },
        ),
        migrations.CreateModel(
            name='Deposit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('amount', models.DecimalField(decimal_places=8, default=0, max_digits=17)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='deposits', to='absortium.Account')),
            ],
        ),
        migrations.CreateModel(
            name='MarketInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('rate', models.DecimalField(decimal_places=8, max_digits=17)),
                ('rate_24h_max', models.DecimalField(decimal_places=8, max_digits=17)),
                ('rate_24h_min', models.DecimalField(decimal_places=8, max_digits=17)),
                ('volume_24h', models.DecimalField(decimal_places=8, default=0, max_digits=17)),
                ('pair', models.CharField(max_length=8)),
            ],
            options={
                'ordering': ('-created',),
            },
        ),
        migrations.CreateModel(
            name='Offer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('system', models.CharField(default='own', max_length=9)),
                ('pair', models.CharField(max_length=8)),
                ('type', models.CharField(max_length=5)),
                ('amount', models.DecimalField(decimal_places=8, default=0, max_digits=26)),
                ('price', models.DecimalField(decimal_places=8, max_digits=17)),
            ],
            options={
                'ordering': ('-price',),
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(default='init', max_length=10)),
                ('system', models.CharField(default='own', max_length=9)),
                ('pair', models.CharField(max_length=8)),
                ('type', models.CharField(max_length=5)),
                ('amount', models.DecimalField(decimal_places=8, default=0, max_digits=17)),
                ('total', models.DecimalField(decimal_places=8, default=0, max_digits=17)),
                ('price', models.DecimalField(decimal_places=8, default=0, max_digits=17)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-price', 'created'],
            },
        ),
        migrations.CreateModel(
            name='Withdrawal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('amount', models.DecimalField(decimal_places=8, default=0, max_digits=17)),
                ('address', models.CharField(max_length=50)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='withdrawals', to='absortium.Account')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='offer',
            unique_together=set([('pair', 'price', 'system', 'type')]),
        ),
        migrations.AlterUniqueTogether(
            name='account',
            unique_together=set([('currency', 'owner', 'address')]),
        ),
    ]
