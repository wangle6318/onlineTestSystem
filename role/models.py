from django.db import models
from django.contrib.auth.models import AbstractUser
from role.save import newStorage
from django.utils.timezone import now
# Create your models here.


class User(AbstractUser):
    sex_choice = (
        (u'male', u'男'),
        (u'female', u'女'),
        (u'nomale', u'保密'),
    )
    job_choice = (
        (u'teacher', u'教师'),
        (u'student', u'学生'),
    )

    name = models.CharField('姓名', max_length=30, blank=True)
    sex = models.CharField('性别', max_length=6, choices=sex_choice, default='nomale')
    phone = models.CharField('手机', max_length=11, null=True, blank=True)
    role = models.CharField('职位', max_length=7, choices=job_choice)
    head_img = models.ImageField('头像', upload_to='head/%Y/%m/', storage=newStorage(), default='head/head_img.jfif')
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    last_modified_time = models.DateTimeField('修改时间', auto_now=True)

    class Meta:
        verbose_name = '用户信息'
        verbose_name_plural = '用户信息管理'
        ordering = ("-last_modified_time", "-created_time")
        indexes = [models.Index(fields=['username']),
                   models.Index(fields=['name'])]

    def __str__(self):
        return str(self.username)


class TeacherStudent(models.Model):
    teacher = models.ForeignKey(User, verbose_name='教师', related_name="teacher_up", on_delete=models.CASCADE)
    student = models.ForeignKey(User, verbose_name='学生', related_name="student_belong", on_delete=models.CASCADE)
    status = models.BooleanField('状态', default=True)
    created_time = models.DateTimeField('创建时间', auto_now_add=True,)
    last_modified_time = models.DateTimeField('修改时间', auto_now=True)

    class Meta:
        unique_together = ('teacher', 'student',)
        verbose_name = '师生关系'
        verbose_name_plural = '师生关系管理'
        ordering = ("-last_modified_time", "-created_time")

    def __str__(self):
        return str(self.id)



