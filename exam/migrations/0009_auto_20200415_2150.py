# Generated by Django 2.2 on 2020-04-15 21:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0008_auto_20200415_2149'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='judgequestion',
            options={'ordering': ('-last_modified_time', '-created_time'), 'verbose_name': '判断试题信息', 'verbose_name_plural': '判断试题信息管理'},
        ),
    ]
