# Generated by Django 2.2.10 on 2020-02-10 10:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('colcon', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='activated',
        ),
        migrations.AddField(
            model_name='profile',
            name='activated',
            field=models.BooleanField(default=False),
        ),
    ]