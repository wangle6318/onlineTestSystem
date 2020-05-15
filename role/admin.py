from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from role.models import *
# Register your models here.


admin.site.site_header = '师生互动平台后台管理系统'
admin.site.site_title = '师生互动平台'


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = ['username', 'name', 'role', 'is_superuser', 'email', 'phone', 'sex', 'created_time',]
    search_fields = ('username', 'name',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('基础信息', {'fields': ('name', 'role', 'sex', 'phone', 'email')}),
        ('权限信息', {'fields': ('is_superuser',)}),
    )
    list_filter = ('role', 'sex',)
    list_per_page = 20
    empty_value_display = ''
    ordering = ['created_time', 'last_modified_time']


@admin.register(TeacherStudent)
class TeacherGroup(admin.ModelAdmin):
    list_display = ['teacher', 'teacher_name', 'student', 'student_name','status',]
    search_fields = ('teacher',)
    list_filter = ('status',)
    list_per_page = 20
    ordering = ['teacher', 'created_time', ]

    def teacher_name(self, obj):
        return obj.teacher.name

    def student_name(self, obj):
        return obj.student.name

    teacher_name.short_description = u'教师姓名'
    student_name.short_description = u'学生姓名'