# Generated by Django 2.2 on 2020-05-04 15:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0023_remove_examinationstatic_uuid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='examinationstatic',
            name='question_num',
        ),
    ]
