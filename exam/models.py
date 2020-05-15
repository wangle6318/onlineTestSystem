from django.db import models
from role.models import User
import django.utils.timezone as timezone
from django.db.models import Sum, Count
import datetime
from django.core.exceptions import ValidationError
from role.save import newStorage
import re
import collections
import random
# Create your models here.

letter = ['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
weight = [2,2,2,2,2,2,2,2,2,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]


class QuestionBank(models.Model):
    type_choice = (
        (u'mc', u'单项选择题'),
        (u'mcs', u'多项选择题'),
        (u'tf', u'判断题'),
    )

    creator = models.ForeignKey(User, verbose_name='创建者', related_name="creator_to", on_delete=models.CASCADE)
    uuid = models.CharField('ID', max_length=12)
    name = models.CharField('题库名称', max_length=50)
    type = models.CharField('题库类型', max_length=6, choices=type_choice, default='mc', blank=False)
    count = models.PositiveIntegerField('题目数量', default=0)
    intro = models.CharField('简介', max_length=300, blank=True)
    status = models.BooleanField('是否生效', default=True)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    last_modified_time = models.DateTimeField('修改时间', auto_now=True)

    def _create_bank_uuid(self):
        year = str(datetime.date.today().year)
        while True:
            uid = year + "".join([str(random.randint(0, 9)) for i in range(6)])
            if not QuestionBank.objects.filter(uuid=uid):
                break
        return uid

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.uuid:
            self.uuid = self._create_bank_uuid()
        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields
        )

    class Meta:
        verbose_name = '题库信息'
        verbose_name_plural = '题库信息管理'
        ordering = ("-last_modified_time", "-created_time")

    def __str__(self):
        return self.name


class SingleQuestion(models.Model):
    uuid = models.CharField('ID', max_length=12)
    bank = models.ForeignKey(QuestionBank, verbose_name='题库', related_name="bank_to", on_delete=models.CASCADE)
    topic = models.TextField('题干', null=False, max_length=1000)
    answer = models.CharField('答案', max_length=5)
    analysis = models.TextField('试题解析', blank=True)
    option_a = models.CharField('A', max_length=300)
    option_b = models.CharField('B', max_length=300)
    option_c = models.CharField('C', max_length=300, null=True, blank=True)
    option_d = models.CharField('D', max_length=300, null=True, blank=True)
    option_e = models.CharField('E', max_length=300, null=True, blank=True)
    option_f = models.CharField('F', max_length=300, null=True, blank=True)
    status = models.BooleanField('是否生效', default=True)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    last_modified_time = models.DateTimeField('修改时间', auto_now=True)

    def _create_singel_question_uuid(self):
        begin = 'mc'
        while True:
            uid = begin + "".join(random.choices(letter, weight, k=6))
            if not SingleQuestion.objects.filter(uuid=uid):
                break
        return uid

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.uuid:
            self.uuid = self._create_singel_question_uuid()
        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields
        )

    def clean(self):
        if self.answer.upper() not in ['A', 'B', 'C', 'D', 'E', 'F']:
            raise ValidationError({'answer': ('答案不符合要求,请填入字母A-F中一个',)})

    def get_img_topic(self):
        imgs = SingleQuestionImg.objects.filter(question__uuid=self.uuid, choice='TOPIC')
        return imgs

    def get_img_a(self):
        img = SingleQuestionImg.objects.filter(question__uuid=self.uuid, choice='A')
        return img

    def get_img_b(self):
        img = SingleQuestionImg.objects.filter(question__uuid=self.uuid, choice='B')
        return img

    def get_img_c(self):
        img = SingleQuestionImg.objects.filter(question__uuid=self.uuid, choice='C')
        return img

    def get_img_d(self):
        img = SingleQuestionImg.objects.filter(question__uuid=self.uuid, choice='D')
        return img

    def get_img_e(self):
        img = SingleQuestionImg.objects.filter(question__uuid=self.uuid, choice='E')
        return img

    def get_img_f(self):
        img = SingleQuestionImg.objects.filter(question__uuid=self.uuid, choice='F')
        return img

    class Meta:
        verbose_name = '单项选择题信息管理'
        verbose_name_plural = '单项选择题信息管理'
        ordering = ("-last_modified_time", "-created_time")

    def __str__(self):
        return str(self.id)


class SingleQuestionImg(models.Model):
    type_choice = (
        (u'TOPIC', u'题干'),
        (u'A', u'A'),
        (u'B', u'B'),
        (u'C', u'C'),
        (u'D', u'D'),
        (u'E', u'E'),
        (u'F', u'F'),
    )
    question = models.ForeignKey(SingleQuestion, verbose_name='题目',
                                 related_name='single_question_to', on_delete=models.CASCADE)
    choice = models.CharField('对应选项', choices=type_choice, max_length=5, null=False)
    intro = models.CharField('图名', max_length=300, blank=True)
    img = models.ImageField('图片', null=False, upload_to='question/%Y/%m/', storage=newStorage())
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    last_modified_time = models.DateTimeField('修改时间', auto_now=True)

    class Meta:
        verbose_name = '单选题图片信息'
        verbose_name_plural = '单选题图片信息管理'
        ordering = ("-last_modified_time", "-created_time")


class MultipleQuestion(models.Model):
    uuid = models.CharField('ID', max_length=12)
    bank = models.ForeignKey(QuestionBank, verbose_name='题库', related_name="multiple_bank_to", on_delete=models.CASCADE)
    topic = models.TextField('题干', null=False, max_length=1000)
    answer = models.CharField('答案', max_length=5)
    analysis = models.TextField('试题解析', blank=True)
    option_a = models.CharField('A', max_length=300)
    option_b = models.CharField('B', max_length=300)
    option_c = models.CharField('C', max_length=300, null=True, blank=True)
    option_d = models.CharField('D', max_length=300, null=True, blank=True)
    option_e = models.CharField('E', max_length=300, null=True, blank=True)
    option_f = models.CharField('F', max_length=300, null=True, blank=True)
    status = models.BooleanField('状态', default=True)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    last_modified_time = models.DateTimeField('修改时间', auto_now=True)\


    def _create_multiple_question_uuid(self):
        begin = 'mcs'
        while True:
            uid = begin + "".join(random.choices(letter, weight, k=5))
            if not MultipleQuestion.objects.filter(uuid=uid):
                break
        return uid

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.uuid:
            self.uuid = self._create_multiple_question_uuid()
        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields
        )

    def clean(self):
        counts = collections.Counter(self.answer.upper())
        if not re.match("[A-F]{1,6}", self.answer.upper()) or max(counts.values()) > 1:
            raise ValidationError({'answer': ('答案不符合要求,请填入字母A-F中一个或多个，不可重复',)})

    def get_img_topic(self):
        imgs = MultipleQuestionImg.objects.filter(question__uuid=self.uuid, choice='TOPIC')
        return imgs

    def get_img_a(self):
        imgs = MultipleQuestionImg.objects.filter(question__uuid=self.uuid, choice='A')
        return imgs

    def get_img_b(self):
        imgs = MultipleQuestionImg.objects.filter(question__uuid=self.uuid, choice='B')
        return imgs

    def get_img_c(self):
        imgs = MultipleQuestionImg.objects.filter(question__uuid=self.uuid, choice='C')
        return imgs

    def get_img_d(self):
        imgs = MultipleQuestionImg.objects.filter(question__uuid=self.uuid, choice='D')
        return imgs

    def get_img_e(self):
        imgs = MultipleQuestionImg.objects.filter(question__uuid=self.uuid, choice='E')
        return imgs

    def get_img_f(self):
        imgs = MultipleQuestionImg.objects.filter(question__uuid=self.uuid, choice='F')
        return imgs

    class Meta:
        verbose_name = '多项选择题信息'
        verbose_name_plural = '多项选择题信息管理'
        ordering = ("-last_modified_time", "-created_time")

    def __str__(self):
        return str(self.id)


class MultipleQuestionImg(models.Model):
    type_choice = (
        (u'TOPIC', u'题干'),
        (u'A', u'A'),
        (u'B', u'B'),
        (u'C', u'C'),
        (u'D', u'D'),
        (u'E', u'E'),
        (u'F', u'F'),
    )
    question = models.ForeignKey(MultipleQuestion, verbose_name='题目',
                                 related_name='multiple_question', on_delete=models.CASCADE)
    choice = models.CharField('对应选项', choices=type_choice, max_length=5, null=False)
    intro = models.CharField('图名', max_length=300, blank=True)
    img = models.ImageField('图片', null=False)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    last_modified_time = models.DateTimeField('修改时间', auto_now=True)

    class Meta:
        verbose_name = '多项选择题图片信息'
        verbose_name_plural = '多项选择题图片信息管理'
        ordering = ("-last_modified_time", "-created_time")


class JudgeQuestion(models.Model):
    answer_choice = (
        (u'1', u'正确'),
        (u'0', u'错误'),
    )
    uuid = models.CharField('ID', max_length=12)
    bank = models.ForeignKey(QuestionBank, verbose_name='题库', related_name="judge_bank_to", on_delete=models.CASCADE)
    topic = models.TextField('题干', null=False, max_length=1000)
    answer = models.CharField('答案', choices=answer_choice, max_length=2, null=False)
    analysis = models.TextField('试题解析', blank=True)
    status = models.BooleanField('状态', default=True)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    last_modified_time = models.DateTimeField('修改时间', auto_now=True)

    def _create_judge_question_uuid(self):
        begin = 'tf'
        while True:
            uid = begin + "".join(random.choices(letter, weight, k=6))
            if not JudgeQuestion.objects.filter(uuid=uid):
                break
        return uid

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.uuid:
            self.uuid = self._create_judge_question_uuid()
        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields
        )

    def get_img_topic(self):
        imgs = JudgeQuestionImg.objects.filter(question__uuid=self.uuid)
        return imgs

    class Meta:
        verbose_name = '判断题信息'
        verbose_name_plural = '判断题信息管理'
        ordering = ("-last_modified_time", "-created_time")

    def __str__(self):
        return str(self.id)


class JudgeQuestionImg(models.Model):
    question = models.ForeignKey(JudgeQuestion, verbose_name='题目',
                                 related_name='judge_question', on_delete=models.CASCADE)
    intro = models.CharField('图名', max_length=300, blank=True)
    img = models.ImageField('图片', null=False)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    last_modified_time = models.DateTimeField('修改时间', auto_now=True)

    class Meta:
        verbose_name = '判断题图片信息'
        verbose_name_plural = '判断题图片信息管理'
        ordering = ("-last_modified_time", "-created_time")


class Examination(models.Model):
    exam_choice = (
        (u'static', u'固定组卷'),
        (u'random', u'随机组卷'),
    )
    status_choice = (
        (u'editor', u'可编辑'),
        (u'publish', u'已发布'),
        (u'view', u'可查阅'),
    )
    uuid = models.CharField('ID', max_length=12)
    creator = models.ForeignKey(User, verbose_name='创建者', related_name="exam_creator_to", on_delete=models.CASCADE)
    title = models.CharField('试卷名称', max_length=100)
    type = models.CharField('组卷类型', choices=exam_choice, max_length=6)
    pass_score = models.PositiveSmallIntegerField('及格分数', default=0)
    time = models.PositiveSmallIntegerField('考试时间', default=0)
    start_time = models.DateTimeField('开始时间', default=timezone.now)
    end_time = models.DateTimeField('结束时间', default=timezone.now)
    status = models.CharField('状态', choices=status_choice, default='editor', max_length=8)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    last_modified_time = models.DateTimeField('修改时间', auto_now=True)

    def _create_examination_uuid(self):
        begin = str(datetime.date.today().year)
        while True:
            uid = begin + "".join(random.choices(letter, weight, k=6))
            if not Examination.objects.filter(uuid=uid):
                break
        return uid

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.uuid:
            self.uuid = self._create_examination_uuid()
        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields
        )

    def get_single_nums(self):
        if self.type == 'random':
            total = ExaminationRandom.objects.filter(exam__uuid=self.uuid, bank__type='mc').aggregate(num=Sum('count'))
            return total['num']
        elif self.type == 'static':
            total = ExaminationStatic.objects.filter(exam__uuid=self.uuid, type='mc').aggregate(num=Count('id'))
            return total['num']

    def get_multiple_nums(self):
        if self.type == 'random':
            total = ExaminationRandom.objects.filter(exam__uuid=self.uuid, bank__type='mcs').aggregate(num=Sum('count'))
            return total['num']
        elif self.type == 'static':
            total = ExaminationStatic.objects.filter(exam__uuid=self.uuid, type='mcs').aggregate(num=Count('id'))
            return total['num']

    def get_judge_nums(self):
        if self.type == 'random':
            total = ExaminationRandom.objects.filter(exam__uuid=self.uuid, bank__type='tf').aggregate(num=Sum('count'))
            return total['num']
        elif self.type == 'static':
            total = ExaminationStatic.objects.filter(exam__uuid=self.uuid, type='tf').aggregate(num=Count('id'))
            return total['num']

    def total_socres(self):
        if self.type == 'random':
            score = 0.0
            exam_randoms = ExaminationRandom.objects.filter(exam__uuid=self.uuid)
            for exam_random in exam_randoms:
                score += exam_random.count * exam_random.score
            return score
        elif self.type == 'static':
            total = ExaminationStatic.objects.filter(exam__uuid=self.uuid).aggregate(num=Sum('score'))
            return total['num']

    class Meta:
        verbose_name = '组卷信息'
        verbose_name_plural = '组卷信息管理'
        ordering = ("-created_time",)

    def __str__(self):
        return self.title


class ExaminationRandom(models.Model):
    uuid = models.CharField('ID', max_length=12)
    exam = models.ForeignKey(Examination, verbose_name='考试', related_name='exam_random_to', on_delete=models.CASCADE)
    bank = models.ForeignKey(QuestionBank, verbose_name='题库', related_name='bank_random_to', on_delete=models.CASCADE)
    count = models.PositiveSmallIntegerField('抽题数量', default=0)
    score = models.FloatField('每题分数', default=0.00)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    last_modified_time = models.DateTimeField('修改时间', auto_now=True)

    def _create_random_examination_uuid(self):
        begin = str(datetime.date.today().year)
        while True:
            uid = begin + "".join(random.choices(letter, weight, k=6))
            if not ExaminationRandom.objects.filter(uuid=uid):
                break
        return uid

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.uuid:
            # if self.bank_id in [exam_r.bank.id for exam_r in self.exam.exam_random_to.all()]:
            #     raise ValidationError({'bank': ('选择的试题库不能重复,重复的题库ID为 %s' % self.bank_id,)})
            self.uuid = self._create_random_examination_uuid()
        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields
        )

    def clean(self):
        if self.count > self.bank.count:
            raise ValidationError({'count': ('抽题数量需小于所选题库数量',)})
        if self.score < 0:
            raise ValidationError({'score': ('每题分数需大于0',)})

    class Meta:
        verbose_name = '随机组卷信息'
        verbose_name_plural = '随机组卷信息'
        ordering = ("created_time",)

    def __str__(self):
        return self.uuid


class ExaminationStatic(models.Model):
    type_choice = (
        (u'mc', u'单项选择题'),
        (u'mcs', u'多项选择题'),
        (u'tf', u'判断题'),
    )

    exam = models.ForeignKey(Examination, verbose_name='考试', related_name='exam_static_to', on_delete=models.CASCADE)
    type = models.CharField('试题类型', max_length=6, choices=type_choice, default='mc')
    single_question = models.ForeignKey(SingleQuestion, verbose_name='单项选择题', related_name='single_static',
                                        on_delete=models.CASCADE, null=True)
    multiple_question = models.ForeignKey(MultipleQuestion, verbose_name='多项选择题', related_name='multiple_static',
                                          on_delete=models.CASCADE, null=True)
    judge_question = models.ForeignKey(JudgeQuestion, verbose_name='判断题', related_name='judge_static',
                                       on_delete=models.CASCADE, null=True)
    score = models.FloatField('每题分数', default=0.00)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    last_modified_time = models.DateTimeField('修改时间', auto_now=True)

    class Meta:
        verbose_name = '固定组卷信息'
        verbose_name_plural = '固定组卷信息'
        ordering = ("created_time",)

    def __str__(self):
        return str(self.id)


class Examiner(models.Model):
    uuid = models.CharField('ID', max_length=12)
    exam = models.ForeignKey(Examination, verbose_name='考试', related_name='exam_examiner', on_delete=models.CASCADE)
    students = models.ForeignKey(User, verbose_name='考试人员', related_name='student_examiner', on_delete=models.CASCADE)
    has_done = models.BooleanField('是否已考', default=False)
    view = models.BooleanField('是否可查阅', default=False)
    limit_count = models.PositiveSmallIntegerField('请求次数', default=0)
    do_start_time = models.DateTimeField('开始答卷时间', null=True, blank=True)
    do_refresh_time = models.DateTimeField('最后刷新时间', null=True, blank=True)
    do_submit_time = models.DateTimeField('交卷时间', null=True, blank=True)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)

    def _create_examiner_uuid(self):
        begin = str(datetime.date.today().year)
        while True:
            uid = begin + "".join(random.choices(letter, weight, k=6))
            if not Examiner.objects.filter(uuid=uid):
                break
        return uid

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.uuid:
            self.uuid = self._create_examiner_uuid()
        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields
        )

    def get_single_num(self):
        total = ExamPaper.objects.filter(examiner__uuid=self.uuid, type='mc').aggregate(num=Count('question_num'))
        return total['num'] if total['num'] else 0

    def get_multiple_num(self):
        total = ExamPaper.objects.filter(examiner__uuid=self.uuid, type='mcs').aggregate(num=Count('question_num'))
        return total['num'] if total['num'] else 0

    def get_judge_num(self):
        total = ExamPaper.objects.filter(examiner__uuid=self.uuid, type='tf').aggregate(num=Count('question_num'))
        return total['num'] if total['num'] else 0

    def get_single_score(self):
        total = ExamPaper.objects.filter(examiner__uuid=self.uuid, type='mc').aggregate(num=Sum('score'))
        return total['num'] if total['num'] else 0

    def get_multiple_score(self):
        total = ExamPaper.objects.filter(examiner__uuid=self.uuid, type='mcs').aggregate(num=Sum('score'))
        return total['num'] if total['num'] else 0

    def get_judge_score(self):
        total = ExamPaper.objects.filter(examiner__uuid=self.uuid, type='tf').aggregate(num=Sum('score'))
        return total['num'] if total['num'] else 0

    def get_test_score(self):
        total = ExamPaper.objects.filter(examiner__uuid=self.uuid, is_true=1).aggregate(num=Sum('score'))
        return total['num'] if total['num'] else 0

    def get_test_time(self):
        examiner = Examiner.objects.get(id=self.id)
        begin = examiner.do_start_time
        end = examiner.do_submit_time
        c = end - begin
        d = c.seconds
        minutes = d // 60
        seconds = d % 60
        time_str = ''
        if minutes >= 10:
            time_str += str(minutes) + ':'
        else:
            time_str += '0' + str(minutes) + ':'
        if seconds >= 10:
            time_str += str(seconds)
        else:
            time_str += '0' + str(seconds)
        return time_str

    def format_time(self):
        examiner = Examiner.objects.get(id=self.id)
        do_time = examiner.do_refresh_time - examiner.do_start_time
        do_ss = do_time.seconds
        time = examiner.exam.time
        time = time * 60 - do_ss
        h, m, s = map(int, str(datetime.timedelta(seconds=time)).split(":"))
        time_str = 'PT'
        if h >= 10:
            time_str += str(h) + 'H'
        else:
            time_str += '0' + str(h) + 'H'
        if m >= 10:
            time_str += str(m) + 'M'
        else:
            time_str += '0' + str(m) + 'M'
        if s >= 10:
            time_str += str(s) + 'S'
        else:
            time_str += '0' + str(s) + 'S'
        return time_str

    class Meta:
        verbose_name = '考试人员信息和试卷管理'
        verbose_name_plural = '考试人员信息和试卷管理'
        ordering = ("-created_time",)


class ExamPaper(models.Model):
    type_choice = (
        (u'mc', u'单项选择题'),
        (u'mcs', u'多项选择题'),
        (u'tf', u'判断题'),
    )

    answer_true = (
        (u'1', u'正确'),
        (u'0', u'错误'),
    )
    question_num = models.PositiveSmallIntegerField('题号', default=0)
    examiner = models.ForeignKey(Examiner, verbose_name='考试信息', related_name='exam_paper', on_delete=models.CASCADE)
    type = models.CharField('试题类型', max_length=6, choices=type_choice, default='mc')
    single_question = models.ForeignKey(SingleQuestion, verbose_name='单项选择题', related_name='single_paper',
                                        on_delete=models.CASCADE, null=True, blank=True)
    multiple_question = models.ForeignKey(MultipleQuestion, verbose_name='多项选择题', related_name='multiple_paper',
                                          on_delete=models.CASCADE, null=True, blank=True)
    judge_question = models.ForeignKey(JudgeQuestion, verbose_name='判断题', related_name='judge_paper',
                                       on_delete=models.CASCADE, null=True, blank=True)
    answer = models.CharField('答案', max_length=10, null=True)
    score = models.FloatField('每题分数', default=0.0)
    is_true = models.CharField('是否正确', max_length=2, choices=answer_true, default='0')

    class Meta:
        verbose_name = '试卷信息'
        verbose_name_plural = '试卷信息管理'
        ordering = ("question_num",)


class ExcelTemplates(models.Model):
    type_choice = (
        (u'st', u'学生'),
        (u'mc', u'单项选择题'),
        (u'mcs', u'多项选择题'),
        (u'tf', u'判断题'),
    )

    name = models.CharField('文件名', max_length=50, null=False)
    file = models.FileField('文件路径', upload_to='excel/%Y/%m', null=False)
    is_static = models.BooleanField('是否是静态模板', default=False)
    type = models.CharField('类型', max_length=6, choices=type_choice, null=False)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = 'EXCEL模板信息'
        verbose_name_plural = 'EXCEL模板信息管理'
        ordering = ("-created_time",)