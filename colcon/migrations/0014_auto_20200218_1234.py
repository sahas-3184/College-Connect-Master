# Generated by Django 2.2.10 on 2020-02-18 07:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('colcon', '0013_complaints'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='complaints',
            name='against_channel',
        ),
        migrations.RemoveField(
            model_name='complaints',
            name='against_person',
        ),
        migrations.RemoveField(
            model_name='complaints',
            name='by',
        ),
    ]
