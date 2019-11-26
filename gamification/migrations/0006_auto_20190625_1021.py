# -*- coding: utf-8 -*-
# Generated by Django 1.11.21 on 2019-06-25 10:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gamification', '0005_auto_20190610_1210'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activitygamificationevent',
            name='activity',
            field=models.ForeignKey(
                            on_delete=django.db.models.deletion.CASCADE,
                            related_name='gamification_events',
                            to='oppia.Activity'),
        ),
        migrations.AlterField(
            model_name='coursegamificationevent',
            name='course',
            field=models.ForeignKey(
                            on_delete=django.db.models.deletion.CASCADE,
                            related_name='gamification_events',
                            to='oppia.Course'),
        ),
        migrations.AlterField(
            model_name='mediagamificationevent',
            name='media',
            field=models.ForeignKey(
                            on_delete=django.db.models.deletion.CASCADE,
                            related_name='gamification_events',
                            to='oppia.Media'),
        ),
    ]
