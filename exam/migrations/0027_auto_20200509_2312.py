# Generated by Django 2.2 on 2020-05-09 23:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0026_examiner_do_refresh_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='examiner',
            name='do_start_time',
            field=models.DateTimeField(null=True, verbose_name='开始答卷时间'),
        ),
        migrations.AlterField(
            model_name='examiner',
            name='do_submit_time',
            field=models.DateTimeField(null=True, verbose_name='交卷时间'),
        ),
    ]
