# Generated by Django 2.2.10 on 2020-02-16 07:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('colcon', '0007_auto_20200212_1143'),
    ]

    operations = [
        migrations.RenameField(
            model_name='post',
            old_name='caption',
            new_name='description',
        ),
    ]
