# Generated by Django 2.2.24 on 2022-04-06 14:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('oppia', '0045_tracker_index'),
        ('summary', '0011_auto_20220317_1706'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserCourseDailySummary',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.DateField()),
                ('type', models.CharField(max_length=15, verbose_name='Activity type')),
                ('time_spent_submitted', models.IntegerField(default=0)),
                ('time_spent_tracked', models.IntegerField(default=0)),
                ('total_submitted', models.IntegerField(default=0)),
                ('total_tracked', models.IntegerField(default=0)),
                ('course', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='oppia.Course')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'UserCourseDailySummary',
                'verbose_name_plural': 'UserCourseDailySummaries',
            },
        ),
    ]
