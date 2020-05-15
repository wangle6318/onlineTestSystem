# Generated by Django 2.2 on 2020-04-08 05:02

import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import role.save


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('name', models.CharField(max_length=30, verbose_name='姓名')),
                ('sex', models.CharField(choices=[('male', '男'), ('female', '女'), ('nomale', '保密')], default='nomale', max_length=5, verbose_name='性别')),
                ('phone', models.CharField(blank=True, max_length=11, null=True, verbose_name='手机')),
                ('role', models.CharField(choices=[('teacher', '教师'), ('student', '学生')], max_length=6, verbose_name='职位')),
                ('head_img', models.ImageField(default='head/head_img.jfif', storage=role.save.newStorage(), upload_to='head/%Y%m/', verbose_name='头像')),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('last_modified_time', models.DateTimeField(auto_now=True, verbose_name='修改时间')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': '用户信息',
                'verbose_name_plural': '用户信息管理',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='TeacherStudent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.BooleanField(default=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_belong', to='role.User', verbose_name='学生')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teacher_up', to='role.User', verbose_name='教师')),
            ],
            options={
                'verbose_name': '师生关系',
                'verbose_name_plural': '师生关系管理',
                'unique_together': {('teacher', 'student')},
            },
        ),
    ]
