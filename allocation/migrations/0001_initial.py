# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-02-22 21:53
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
            name='AggregatedPortfolio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('start_date', models.DateField()),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('codec', models.CharField(max_length=8, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Objective',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('finalValue', models.FloatField()),
                ('time_horizon', models.IntegerField()),
                ('finality', models.CharField(max_length=300)),
                ('priority', models.IntegerField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ObjectivePortfolioAsset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('quote', models.FloatField()),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='allocation.Asset')),
            ],
        ),
        migrations.CreateModel(
            name='ObjectiveSolution',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('expected_return', models.FloatField()),
                ('expected_risk', models.FloatField()),
                ('savings_required', models.FloatField()),
                ('feasible', models.BooleanField()),
                ('objective', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='allocation.Objective')),
            ],
        ),
        migrations.CreateModel(
            name='PortfolioAsset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('quote', models.FloatField()),
                ('aggregated_portfolio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='allocation.AggregatedPortfolio')),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='allocation.Asset')),
            ],
        ),
        migrations.CreateModel(
            name='Series',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('price', models.FloatField()),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='allocation.Asset')),
            ],
        ),
        migrations.CreateModel(
            name='UserResource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('founds', models.FloatField()),
                ('monthly_savings', models.FloatField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='objectiveportfolioasset',
            name='objective_solution',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='allocation.ObjectiveSolution'),
        ),
    ]
