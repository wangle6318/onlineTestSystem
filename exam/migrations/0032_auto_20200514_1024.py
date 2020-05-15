# Generated by Django 2.2 on 2020-05-14 10:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0031_auto_20200512_2039'),
    ]

    operations = [
        migrations.AlterField(
            model_name='examinationstatic',
            name='judge_question',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='judge_static', to='exam.JudgeQuestion', verbose_name='判断题'),
        ),
        migrations.AlterField(
            model_name='examinationstatic',
            name='multiple_question',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='multiple_static', to='exam.MultipleQuestion', verbose_name='多项选择题'),
        ),
        migrations.AlterField(
            model_name='examinationstatic',
            name='single_question',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='single_static', to='exam.SingleQuestion', verbose_name='单项选择题'),
        ),
        migrations.AlterField(
            model_name='examiner',
            name='do_refresh_time',
            field=models.DateTimeField(blank=True, null=True, verbose_name='最后刷新时间'),
        ),
        migrations.AlterField(
            model_name='examiner',
            name='do_start_time',
            field=models.DateTimeField(blank=True, null=True, verbose_name='开始答卷时间'),
        ),
        migrations.AlterField(
            model_name='examiner',
            name='do_submit_time',
            field=models.DateTimeField(blank=True, null=True, verbose_name='交卷时间'),
        ),
        migrations.AlterField(
            model_name='exampaper',
            name='judge_question',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='judge_paper', to='exam.JudgeQuestion'),
        ),
        migrations.AlterField(
            model_name='exampaper',
            name='multiple_question',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='multiple_paper', to='exam.MultipleQuestion'),
        ),
        migrations.AlterField(
            model_name='exampaper',
            name='single_question',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='single_paper', to='exam.SingleQuestion'),
        ),
    ]
