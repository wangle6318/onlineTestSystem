from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from exam.models import *
# Register your models here.


@admin.register(ExcelTemplates)
class ExcelTemplatesAdmin(admin.ModelAdmin):
    list_display = ['name', 'file', 'is_static', 'type', 'created_time', ]
    search_fields = ('name',)
    list_filter = ('type',)
    list_per_page = 20
    ordering = ['created_time', ]


@admin.register(QuestionBank)
class QuestionBankAdmin(admin.ModelAdmin):
    list_display = ['creator', 'creator_name', 'uuid', 'name', 'type', 'count', 'intro', 'status', 'created_time']
    search_fields = ('name',)
    list_filter = ('type', 'status')
    list_per_page = 20
    ordering = ['created_time', ]
    list_display_links = ('uuid', 'name',)
    date_hierarchy = 'created_time'
    readonly_fields = ['type', 'uuid']
    fields1 = ['uuid', 'creator', 'name', 'type', 'count', 'intro', 'status', ]
    fields2 = ['creator', 'name', 'type', 'count', 'intro', 'status', ]

    def creator_name(self, obj):
        return obj.creator.name

    creator_name.short_description = u'创建人姓名'

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields
        else:
            return ['count',]

    def get_fields(self, request, obj=None):
        if obj:
            return self.fields1
        else:
            return self.fields2

    def has_delete_permission(self, request, obj=None):
        return False

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        限制creator能选择的范围（所有职业为教师的用户）
        :param db_field:
        :param request:
        :param kwargs:
        :return:
        """
        if db_field.name == "creator":
            kwargs["queryset"] = User.objects.filter(role='teacher')
        return super(QuestionBankAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class SingleQuestionImgInline(admin.TabularInline):
    model = SingleQuestionImg
    extra = 0


@admin.register(SingleQuestion)
class SingleQuestionAdmin(admin.ModelAdmin):
    list_display = ['uuid', 'bank', 'topic', 'option_a', 'option_b', 'option_c', 'option_d',
                    'option_e', 'option_f', 'answer', 'analysis', 'last_modified_time']
    search_fields = ('topic',)
    list_filter = ()
    list_per_page = 20
    ordering = ['created_time', ]
    list_display_links = ('uuid', 'bank')
    date_hierarchy = 'created_time'
    readonly_fields = ['uuid', 'bank']
    empty_value_display = ''
    inlines = [SingleQuestionImgInline, ]
    fieldsets1 = (
        (None, {'fields': ('uuid', 'bank', 'topic')}),
        ('选项信息', {'fields': ('option_a', 'option_b', 'option_c', 'option_d', 'option_e', 'option_f')}),
        ('答案解析', {'fields': ('answer', 'analysis')}),
        ('状态', {'fields': ('status',)}),
    )

    fieldsets2 = (
        (None, {'fields': ('bank', 'topic')}),
        ('选项信息', {'fields': ('option_a', 'option_b', 'option_c', 'option_d', 'option_e', 'option_f')}),
        ('答案解析', {'fields': ('answer', 'analysis')}),
        ('状态', {'fields': ('status',)}),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields
        else:
            return []

    def get_fieldsets(self, request, obj=None):
        if obj:
            return self.fieldsets1
        else:
            return self.fieldsets2

    def has_delete_permission(self, request, obj=None):
        return False

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "bank":
            kwargs["queryset"] = QuestionBank.objects.filter(type='mc')
        return super(SingleQuestionAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if change:
            if 'status' in form.changed_data:
                if obj.status:
                    bank = obj.bank
                    bank.count += 1
                    bank.save()
                else:
                    bank = obj.bank
                    bank.count -= 1
                    bank.save()
        else:
            if obj.status:
                bank = obj.bank
                bank.count += 1
                bank.save()
        super().save_model(request, obj, form, change)


class MultipleQuestionImgInline(admin.TabularInline):
    model = MultipleQuestionImg
    extra = 0


@admin.register(MultipleQuestion)
class MultipleQuestionAdmin(admin.ModelAdmin):
    list_display = ['uuid', 'bank', 'topic', 'option_a', 'option_b', 'option_c', 'option_d',
                    'option_e', 'option_f', 'answer', 'analysis', 'last_modified_time']
    search_fields = ('topic',)
    list_filter = ()
    list_per_page = 20
    ordering = ['created_time', ]
    list_display_links = ('uuid', 'bank')
    date_hierarchy = 'created_time'
    readonly_fields = ['uuid', 'bank']
    empty_value_display = ''
    inlines = [MultipleQuestionImgInline, ]
    fieldsets1 = (
        (None, {'fields': ('uuid', 'bank', 'topic')}),
        ('选项信息', {'fields': ('option_a', 'option_b', 'option_c', 'option_d', 'option_e', 'option_f')}),
        ('答案解析', {'fields': ('answer', 'analysis')}),
    )

    fieldsets2 = (
        (None, {'fields': ('bank', 'topic')}),
        ('选项信息', {'fields': ('option_a', 'option_b', 'option_c', 'option_d', 'option_e', 'option_f')}),
        ('答案解析', {'fields': ('answer', 'analysis')}),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields
        else:
            return []

    def get_fieldsets(self, request, obj=None):
        if obj:
            return self.fieldsets1
        else:
            return self.fieldsets2

    def has_delete_permission(self, request, obj=None):
        return False

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "bank":
            kwargs["queryset"] = QuestionBank.objects.filter(type='mcs')
        return super(MultipleQuestionAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if change:
            if 'status' in form.changed_data:
                if obj.status:
                    bank = obj.bank
                    bank.count += 1
                    bank.save()
                else:
                    bank = obj.bank
                    bank.count -= 1
                    bank.save()
        else:
            if obj.status:
                bank = obj.bank
                bank.count += 1
                bank.save()
        super().save_model(request, obj, form, change)


class JudgeQuestionImgInline(admin.TabularInline):
    model = JudgeQuestionImg
    extra = 0


@admin.register(JudgeQuestion)
class JudgeQuestionAdmin(admin.ModelAdmin):
    list_display = ['uuid', 'bank', 'topic', 'answer', 'analysis', 'last_modified_time']
    search_fields = ('topic',)
    list_filter = ()
    list_per_page = 20
    ordering = ['created_time', ]
    list_display_links = ('uuid', 'bank')
    date_hierarchy = 'created_time'
    readonly_fields = ['uuid', 'bank']
    empty_value_display = ''
    inlines = [JudgeQuestionImgInline, ]
    fieldsets1 = (
        (None, {'fields': ('uuid', 'bank', 'topic')}),
        ('答案解析', {'fields': ('answer', 'analysis')}),
    )

    fieldsets2 = (
        (None, {'fields': ('bank', 'topic')}),
        ('答案解析', {'fields': ('answer', 'analysis')}),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields
        else:
            return []

    def get_fieldsets(self, request, obj=None):
        if obj:
            return self.fieldsets1
        else:
            return self.fieldsets2

    def has_delete_permission(self, request, obj=None):
        return False

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "bank":
            kwargs["queryset"] = QuestionBank.objects.filter(type='tf')
        return super(JudgeQuestionAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if change:
            if 'status' in form.changed_data:
                if obj.status:
                    bank = obj.bank
                    bank.count += 1
                    bank.save()
                else:
                    bank = obj.bank
                    bank.count -= 1
                    bank.save()
        else:
            if obj.status:
                bank = obj.bank
                bank.count += 1
                bank.save()
        super().save_model(request, obj, form, change)


class ExaminationRandomInline(admin.TabularInline):
    model = ExaminationRandom
    fk_name = "exam"
    readonly_fields = ['uuid', 'bank_type']
    fields = ['uuid', 'bank', 'bank_type', 'count', 'score']
    empty_value_display = ''
    raw_id_fields = ("bank",)
    extra = 0

    def bank_type(self, obj):
        if obj.bank.type == 'mc':
            return '单项选择题'
        elif obj.bank.type == 'mcs':
            return '多项选择题'
        elif obj.bank.type == 'tf':
            return '判断题'

    bank_type.short_description = u'题库类型'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "bank":
            kwargs["queryset"] = QuestionBank.objects.filter(status=True)
        return super(ExaminationRandomInline, self).formfield_for_foreignkey(db_field, request, **kwargs)


class ExaminationStaticInline(admin.TabularInline):
    model = ExaminationStatic
    fk_name = "exam"
    extra = 0
    raw_id_fields = ("single_question", 'multiple_question', 'judge_question',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "single_question":
            kwargs["queryset"] = SingleQuestion.objects.filter(status=True)
        if db_field.name == "multiple_question":
            kwargs["queryset"] = MultipleQuestion.objects.filter(status=True)
        if db_field.name == "judge_question":
            kwargs["queryset"] = JudgeQuestion.objects.filter(status=True)
        return super(ExaminationStaticInline, self).formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Examination)
class ExaminationAdmin(admin.ModelAdmin):
    list_display = ['uuid', 'title', 'creator_name', 'type', 'total_score', 'pass_score', 'time', 'start_time',
                    'end_time', 'status', 'created_time']
    search_fields = ('title',)
    list_filter = ('type',)
    list_per_page = 20
    ordering = ['created_time', ]
    list_display_links = ('uuid', 'title')
    date_hierarchy = 'created_time'
    readonly_fields = ['uuid', 'type']
    empty_value_display = ''
    fieldsets1 = (
        (None, {'fields': ('uuid', 'title', 'creator', 'type')}),
        ('基本信息', {'fields': ('pass_score', 'time', 'start_time', 'end_time')}),
        ('状态信息', {'fields': ('status',)}),
    )

    fieldsets2 = (
        (None, {'fields': ('title', 'creator', 'type')}),
        ('基本信息', {'fields': ('pass_score', 'time', 'start_time', 'end_time')}),
        ('状态信息', {'fields': ('status',)}),
    )

    def creator_name(self, obj):
        return obj.creator.name

    creator_name.short_description = u'创建人姓名'

    def total_score(self, obj):
        return obj.total_socres()

    total_score.short_description = u'总分'

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields
        else:
            return []

    def get_fieldsets(self, request, obj=None):
        if obj:
            return self.fieldsets1
        else:
            return self.fieldsets2

    def get_inline_instances(self, request, obj=None):
        if obj:
            if obj.type == 'static':
                self.inlines = [ExaminationStaticInline, ]
            else:
                self.inlines = [ExaminationRandomInline, ]
        return super(ExaminationAdmin, self).get_inline_instances(request, obj)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "creator":
            kwargs["queryset"] = User.objects.filter(role='teacher')
        return super(ExaminationAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class ExamPaperInline(admin.TabularInline):
    model = ExamPaper
    fk_name = "examiner"
    readonly_fields = ('question_num', 'type', 'question_topic', 'answer', 'score', 'is_true',)
    fields = ('question_num', 'type', 'question_topic', 'answer', 'score', 'is_true',)
    extra = 0
    empty_value_display = ''
    raw_id_fields = ("single_question", 'multiple_question', 'judge_question',)

    def question_topic(self, obj):
        if obj:
            if obj.type == 'mc':
                return obj.single_question.topic
            elif obj.type == 'mcs':
                return obj.multiple_question.topic
            elif obj.type == 'tf':
                return obj.judge_question.topic

    question_topic.short_description = u'题干'

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

@admin.register(Examiner)
class ExaminerAdmin(admin.ModelAdmin):
    list_display = ['uuid', 'exam', 'students', 'has_done', 'view', 'limit_count', 'do_start_time', 'do_refresh_time',
                    'do_submit_time', ]
    list_filter = ('has_done', 'view',)
    list_per_page = 20
    ordering = ['created_time', ]
    list_display_links = ('uuid',)
    date_hierarchy = 'created_time'
    readonly_fields = ['uuid', 'exam', 'students']
    empty_value_display = ''
    inlines = [ExamPaperInline, ]
    raw_id_fields = ['students',]
    fieldsets1 = (
        (None, {'fields': ('uuid', 'exam', 'students',)}),
        ('状态信息', {'fields': ('has_done', 'view', 'limit_count',)}),
        ('考试时间', {'fields': ('do_start_time', 'do_refresh_time', 'do_submit_time')}),
    )

    fieldsets2 = (
        (None, {'fields': ('exam', 'students',)}),
        ('状态信息', {'fields': ('has_done', 'view', 'limit_count',)}),
        ('考试时间', {'fields': ('do_start_time', 'do_refresh_time', 'do_submit_time')}),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields
        else:
            return []

    def get_fieldsets(self, request, obj=None):
        if obj:
            return self.fieldsets1
        else:
            return self.fieldsets2

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
