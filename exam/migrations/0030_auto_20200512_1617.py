# Generated by Django 2.2 on 2020-05-12 16:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0029_auto_20200512_1616'),
    ]

    operations = [
        migrations.AlterField(
            model_name='singlequestionimg',
            name='intro',
            field=models.CharField(blank=True, max_length=300, verbose_name='图名'),
        ),
    ]
