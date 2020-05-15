from django.shortcuts import render, redirect, get_object_or_404, HttpResponse, Http404, get_list_or_404
from django.views.generic import View
from exam.models import QuestionBank, SingleQuestion, SingleQuestionImg, MultipleQuestion, MultipleQuestionImg, \
    JudgeQuestion, JudgeQuestionImg, Examination, ExaminationRandom, ExaminationStatic, Examiner, \
    ExamPaper, ExcelTemplates
from role.models import TeacherStudent, User
from django.db import transaction, IntegrityError
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Max
from django.db.models import Q
import json
import random
from xlrd import open_workbook
from xlwt import Workbook
from exam.img_save import SaveImg
from datetime import datetime
from django.utils import timezone
# Create your views here.


class LoginRequiredMixin(object):
    """登录状态校验"""
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)


class GetTeacherIndex(LoginRequiredMixin, View):
    def get(self, request):
        exams = Examination.objects.filter((Q(end_time__lt=timezone.now()) & Q(status='publish')) | Q(status='view'), creator=request.user)
        return render(request, 'exam/conservator.html', {"exams": exams})


class GetQuestionBank(LoginRequiredMixin, View):
    def get(self, request):
        banks = QuestionBank.objects.filter(creator=request.user, status=True)
        return render(request, 'exam/banks.html', {"banks": banks})


class AddQuestionBank(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'exam/bankadd.html')

    def post(self, request):
        title = request.POST.get('bank-name')
        title = title.replace(' ', '')
        if title:
            btype = request.POST.get('bank-type')
            intro = request.POST.get('bank-intro')
            QuestionBank.objects.create(creator=request.user, name=title, type=btype, intro=intro)
            return redirect('exam:getbank')
        else:
            return redirect('exam:addbank')


class DeleteQuestionBank(LoginRequiredMixin, View):
    def get(self, request):
        uid = request.GET.get('slug')
        if uid:
            questionbank = get_object_or_404(QuestionBank, creator=request.user, uuid=uid)
            questionbank.status = False
            questionbank.save()
        return redirect('exam:getbank')


class GetQuestions(LoginRequiredMixin, View):
    def get(self, request):
        buuid = request.GET.get('slug')
        bank = get_object_or_404(QuestionBank, uuid=buuid, status=True)
        if bank.type == 'mc':
            questions = SingleQuestion.objects.filter(bank=bank, status=True)
            return render(request, 'exam/questions.html', {"questions": questions, "bank": bank})
        elif bank.type == 'mcs':
            questions = MultipleQuestion.objects.filter(bank=bank, status=True)
            return render(request, 'exam/questions.html', {"questions": questions, "bank": bank})
        elif bank.type == 'tf':
            questions = JudgeQuestion.objects.filter(bank=bank, status=True)
            return render(request, 'exam/questions.html', {"questions": questions, "bank": bank})


class GetQuestion(LoginRequiredMixin, View):
    def get(self, request):
        host = request.get_host()
        bank = get_object_or_404(QuestionBank, uuid=request.GET.get('bank-uid'), status=True)
        txt = []
        other = []
        imgs = [[], [], [], [], [], [], []]
        if bank.type == 'mc':
            question = get_object_or_404(SingleQuestion, uuid=request.GET.get('question-uid'), status=True)
            # question = SingleQuestion.objects.get(uuid='md2v4roj')
            topic = question.topic
            answer = question.answer
            analysis = question.analysis
            other.append(answer)
            other.append(analysis)
            txt.append(topic)
            for x in ['a', 'b', 'c', 'd', 'e', 'f']:
                tmp = eval('question.option_' + (x))
                if tmp:
                    txt.append(tmp)
            imgQuery = SingleQuestionImg.objects.filter(question=question)
            for query in imgQuery:
                for index, choice in enumerate(['TOPIC', 'A', 'B', 'C', 'D', 'E', 'F']):
                    if query.choice == choice:
                        imgs[index].append('http://'+host+'/media/' + str(query.img))
                        break
        elif bank.type == 'mcs':
            question = get_object_or_404(MultipleQuestion, uuid=request.GET.get('question-uid'), status=True)
            topic = question.topic
            answer = question.answer
            analysis = question.analysis
            other.append(answer)
            other.append(analysis)
            txt.append(topic)
            for x in ['a', 'b', 'c', 'd', 'e', 'f']:
                tmp = eval('question.option_' + (x))
                if tmp:
                    txt.append(tmp)
            imgQuery = MultipleQuestionImg.objects.filter(question=question)
            for query in imgQuery:
                for index, choice in enumerate(['TOPIC', 'A', 'B', 'C', 'D', 'E', 'F']):
                    if query.choice == choice:
                        imgs[index].append('http://' + host + '/media/' + str(query.img))
                        break
        elif bank.type == 'tf':
            question = get_object_or_404(JudgeQuestion, uuid=request.GET.get('question-uid'), status=True)
            topic = question.topic
            answer = question.answer
            analysis = question.analysis
            other.append(answer)
            other.append(analysis)
            txt.append(topic)
            imgQuery = JudgeQuestionImg.objects.filter(question=question)
            for query in imgQuery:
                imgs[0].append('http://' + host + '/media/' + str(query.img))
        return HttpResponse(json.dumps({"status": 1, "message": "sucess", "txt": txt, "other": other, "imgs": imgs}))


class AddQuestion(LoginRequiredMixin, View):
    def post(self, request):
        host = request.get_host()
        bank = get_object_or_404(QuestionBank, uuid=request.POST.get('bank-uid'))
        status = 1
        message = "保存成功"
        quid = ""
        img_list = []
        url_list = []
        if bank.type == 'mc':
            try:
                with transaction.atomic():
                    quid = request.POST.get('question-uid')
                    topic = request.POST.get('txtQuestion')
                    a = request.POST.get('txtQuestionOptionA')
                    b = request.POST.get('txtQuestionOptionB')
                    c = request.POST.get('txtQuestionOptionC')
                    d = request.POST.get('txtQuestionOptionD')
                    e = request.POST.get('txtQuestionOptionE')
                    f = request.POST.get('txtQuestionOptionF')
                    answer = request.POST.get('trueOption')
                    analysis = request.POST.get('txtAnalysis')
                    if quid:
                        question = get_object_or_404(SingleQuestion, uuid=quid)
                        question.topic = topic
                        question.option_a = a
                        question.option_b = b
                        question.option_c = c
                        question.option_d = d
                        question.option_e = e
                        question.option_f = f
                        question.answer = answer
                        question.analysis = analysis
                        question.save()
                    else:
                        question = SingleQuestion.objects.create(bank=bank,
                                                                 topic=topic, option_a=a, option_b=b, option_c=c, option_d=d,
                                                                 option_e=e, option_f=f, answer=answer, analysis=analysis)
                        quid = question.uuid
                        bank.count += 1
                        bank.save()
                    if len(request.FILES):
                        for key in request.FILES.keys():
                            img_list.append(key)
                            choices = ['txt', 'A', 'B', 'C', 'D', 'E', 'F']
                            for choice in choices:
                                if choice in key:
                                    file = request.FILES.get(key, None)
                                    if file:
                                        save_path = SaveImg().img_save(file, 'question')
                                        if choice == 'txt':
                                            imgs = SingleQuestionImg.objects.create(question=question, choice='TOPIC', intro=file.name,
                                                                         img=save_path.split("media\\")[-1])
                                        else:
                                            imgs = SingleQuestionImg.objects.create(question=question, choice=choice, intro=file.name,
                                                                             img=save_path.split("media\\")[-1])
                                        url_list.append('http://' + host + '/media/' + str(imgs.img))
                                    break
            except IntegrityError:
                status = 0
                message = "保存失败，请重试"
        elif bank.type == 'mcs':
            try:
                with transaction.atomic():
                    quid = request.POST.get('question-uid')
                    topic = request.POST.get('txtQuestion')
                    a = request.POST.get('txtQuestionOptionA')
                    b = request.POST.get('txtQuestionOptionB')
                    c = request.POST.get('txtQuestionOptionC')
                    d = request.POST.get('txtQuestionOptionD')
                    e = request.POST.get('txtQuestionOptionE')
                    f = request.POST.get('txtQuestionOptionF')
                    answer = "".join(request.POST.getlist('trueOption'))
                    analysis = request.POST.get('txtAnalysis')
                    if quid:
                        question = get_object_or_404(MultipleQuestion, uuid=quid)
                        question.topic = topic
                        question.option_a = a
                        question.option_b = b
                        question.option_c = c
                        question.option_d = d
                        question.option_e = e
                        question.option_f = f
                        question.answer = answer
                        question.analysis = analysis
                        question.save()
                    else:
                        question = MultipleQuestion.objects.create(bank=bank,
                                                                 topic=topic, option_a=a, option_b=b, option_c=c, option_d=d,
                                                                 option_e=e, option_f=f, answer=answer, analysis=analysis)
                        quid = question.uuid
                        bank.count += 1
                        bank.save()
                    if len(request.FILES):
                        for key in request.FILES.keys():
                            img_list.append(key)
                            choices = ['txt', 'A', 'B', 'C', 'D', 'E', 'F']
                            for choice in choices:
                                if choice in key:
                                    file = request.FILES.get(key, None)
                                    if file:
                                        save_path = SaveImg().img_save(file, 'question')
                                        if choice == 'txt':
                                            imgs = MultipleQuestionImg.objects.create(question=question, choice='TOPIC', intro=file.name,
                                                                         img=save_path.split("media\\")[-1])
                                        else:
                                            imgs = MultipleQuestionImg.objects.create(question=question, choice=choice, intro=file.name,
                                                                             img=save_path.split("media\\")[-1])
                                        url_list.append('http://' + host + '/media/' + str(imgs.img))
                                    break
            except IntegrityError:
                status = 0
                message = "保存失败，请重试"
        elif bank.type == 'tf':
            try:
                with transaction.atomic():
                    quid = request.POST.get('question-uid')
                    topic = request.POST.get('txtQuestion')
                    answer = request.POST.get('trueOption')
                    analysis = request.POST.get('txtAnalysis')
                    if quid:
                        question = get_object_or_404(JudgeQuestion, uuid=quid)
                        question.topic = topic
                        question.answer = answer
                        question.analysis = analysis
                        question.save()
                    else:
                        question = JudgeQuestion.objects.create(bank=bank,
                                                                 topic=topic, answer=answer, analysis=analysis)
                        quid = question.uuid
                        bank.count += 1
                        bank.save()
                    if len(request.FILES):
                        for key in request.FILES.keys():
                            img_list.append(key)
                            file = request.FILES.get(key, None)
                            if file:
                                save_path = SaveImg().img_save(file, 'question')
                                imgs = JudgeQuestionImg.objects.create(question=question, intro=file.name, img=save_path.split("media\\")[-1])
                                url_list.append('http://' + host + '/media/' + str(imgs.img))
            except IntegrityError:
                status = 0
                message = "保存失败，请重试"
        return HttpResponse(json.dumps({"status": status, "message": message, "quid": quid, "imgs": img_list, "urls": url_list}))


class BatchAddQuestion(LoginRequiredMixin, View):
    def post(self, request):
        file = request.FILES.get('file', None)
        buuid = request.POST.get('uuid', None)
        bank = QuestionBank.objects.get(uuid=buuid)
        from uuid import uuid1
        save_path = SaveImg().excel_save(file, 'excel')
        readboot = open_workbook(save_path)
        sheet = readboot.sheet_by_index(0)
        # 获取excel的行和列
        nrows = sheet.nrows
        ncols = sheet.ncols
        row = sheet.row_values(0)
        row.append("结果")
        write_list = []
        write_list.append(row)
        excel_type = ''
        result_name = ''
        if bank.type == 'mc':
            excel_type = 'mc'
            result_name = '单项选择题上传模板-导入结果'
            for i in range(1, nrows):
                row = sheet.row_values(i)
                topic = row[0]
                if not topic:
                    row.append("题干不能为空，插入失败")
                    write_list.append(row)
                    continue
                elif type(topic) is not str:
                    topic = str(int(float(topic)))
                a = row[1]
                if not a:
                    row.append("选项A不能为空，插入失败")
                    write_list.append(row)
                    continue
                elif type(a) is not str:
                    a = str(int(float(a)))
                b = row[2]
                if not b:
                    row.append("选项B不能为空，插入失败")
                    write_list.append(row)
                    continue
                elif type(b) is not str:
                    b = str(int(float(b)))
                c = row[3]
                if type(c) is not str:
                    c = str(int(float(c)))
                d = row[4]
                if type(d) is not str:
                    d = str(int(float(d)))
                e = row[5]
                if type(e) is not str:
                    e = str(int(float(e)))
                f = row[6]
                if type(f) is not str:
                    f = str(int(float(f)))
                answer = row[7]
                if answer not in ['A', 'B', 'C', 'D', 'E', 'F']:
                    row.append("答案不符合要求，插入失败")
                    write_list.append(row)
                    continue
                analysis = row[8]
                try:
                    with transaction.atomic():
                        SingleQuestion.objects.create(bank=bank,
                                                      topic=topic, option_a=a, option_b=b, option_c=c, option_d=d,
                                                      option_e=e, option_f=f, answer=answer, analysis=analysis)
                        bank.count += 1
                        bank.save()
                except IntegrityError:
                    row.append("添加失败")
                else:
                    row.append("添加成功")
                finally:
                    write_list.append(row)
        elif bank.type == 'mcs':
            excel_type = 'mcs'
            result_name = '多项选择题上传模板-导入结果'
            for i in range(1, nrows):
                row = sheet.row_values(i)
                topic = row[0]
                if not topic:
                    row.append("题干不能为空，插入失败")
                    write_list.append(row)
                    continue
                elif type(topic) is not str:
                    topic = str(int(float(topic)))
                a = row[1]
                if not a:
                    row.append("选项A不能为空，插入失败")
                    write_list.append(row)
                    continue
                elif type(a) is not str:
                    a = str(int(float(a)))
                b = row[2]
                if not b:
                    row.append("选项B不能为空，插入失败")
                    write_list.append(row)
                    continue
                elif type(b) is not str:
                    b = str(int(float(b)))
                c = row[3]
                if type(c) is not str:
                    c = str(int(float(c)))
                d = row[4]
                if type(d) is not str:
                    d = str(int(float(d)))
                e = row[5]
                if type(e) is not str:
                    e = str(int(float(e)))
                f = row[6]
                if type(f) is not str:
                    f = str(int(float(f)))
                answer = row[7]
                if not answer.isalpha():
                    row.append("答案不符合要求，插入失败")
                    write_list.append(row)
                    continue
                analysis = row[8]
                try:
                    with transaction.atomic():
                        MultipleQuestion.objects.create(bank=bank,
                                                        topic=topic, option_a=a, option_b=b, option_c=c, option_d=d,
                                                        option_e=e, option_f=f, answer=answer, analysis=analysis)
                        bank.count += 1
                        bank.save()
                except IntegrityError:
                    row.append("添加失败")
                else:
                    row.append("添加成功")
                finally:
                    write_list.append(row)
        elif bank.type == 'tf':
            excel_type = 'tf'
            result_name = '判断题上传模板-导入结果'
            for i in range(1, nrows):
                row = sheet.row_values(i)
                topic = row[0]
                if not topic:
                    row.append("题干不能为空，插入失败")
                    write_list.append(row)
                    continue
                answer = row[1]
                if answer == 'T':
                    answer = '1'
                elif answer == 'F':
                    answer = '0'
                else:
                    row.append("答案不符合要求，插入失败")
                    write_list.append(row)
                    continue
                analysis = row[2]

                try:
                    with transaction.atomic():
                        JudgeQuestion.objects.create(bank=bank,
                                                     topic=topic, answer=answer, analysis=analysis)
                        bank.count += 1
                        bank.save()
                except IntegrityError:
                    row.append("添加失败")
                else:
                    row.append("添加成功")
                finally:
                    write_list.append(row)
        SaveImg().delete_question_img(save_path)
        workbook = Workbook(encoding='utf-8')
        sheet = workbook.add_sheet('sheet1')
        for i in range(len(write_list)):
            for j in range(len(write_list[0])):
                sheet.write(i, j, write_list[i][j])
        path = SaveImg().get_img_path('excel') + str(uuid1()) + ".xls"
        workbook.save(path)
        excel = ExcelTemplates.objects.create(name=result_name, type=excel_type, file=path.split("media\\")[-1])
        host = request.get_host()
        address = 'http://' + host + '/role/downloadexcel/' + str(excel.id)
        return HttpResponse(json.dumps({"status": 1, "address": address, "name": result_name}))



class DeleteTopicImg(LoginRequiredMixin, View):
    def get(self, request):
        bank = get_object_or_404(QuestionBank, uuid=request.GET.get('bank-uid'))
        path = request.GET.get('path')
        path1 = path.split("/")[-1]
        path2 =  path.split("\\")[-1]
        option = request.GET.get('option')
        status = 1
        message = "删除成功"
        if bank.type == 'mc':
            question = get_object_or_404(SingleQuestion, uuid=request.GET.get('question-uid'))
            for choice in ['txt', 'A', 'B', 'C', 'D', 'E', 'F']:
                if choice in option:
                    if choice == 'txt':
                        imgs = SingleQuestionImg.objects.filter(question=question, choice='TOPIC')
                    else:
                        imgs = SingleQuestionImg.objects.filter(question=question, choice=choice)
                    for img in imgs:
                        if path1 == str(img.img).split("/")[-1]:
                            SaveImg().delete_question_img(str(img.img))
                            img.delete()
                        elif path2 == str(img.img).split("\\")[-1]:
                            SaveImg().delete_question_img(str(img.img))
                            img.delete()
                    break
        elif bank.type == 'mcs':
            question = get_object_or_404(MultipleQuestion, uuid=request.GET.get('question-uid'))
            for choice in ['txt', 'A', 'B', 'C', 'D', 'E', 'F']:
                if choice in option:
                    if choice == 'txt':
                        imgs = MultipleQuestionImg.objects.filter(question=question, choice='TOPIC')
                    else:
                        imgs = MultipleQuestionImg.objects.filter(question=question, choice=choice)
                    for img in imgs:
                        if path1 == str(img.img).split("/")[-1]:
                            SaveImg().delete_question_img(str(img.img))
                            img.delete()
                        elif path2 == str(img.img).split("\\")[-1]:
                            SaveImg().delete_question_img(str(img.img))
                            img.delete()
                    break
        elif bank.type == 'tf':
            question = get_object_or_404(JudgeQuestion, uuid=request.GET.get('question-uid'))
            imgs = JudgeQuestionImg.objects.filter(question=question)
            for img in imgs:
                if path1 == str(img.img).split("/")[-1]:
                    SaveImg().delete_question_img(str(img.img))
                    img.delete()
                elif path2 == str(img.img).split("\\")[-1]:
                    SaveImg().delete_question_img(str(img.img))
                    img.delete()
        return HttpResponse(json.dumps({"status": status, "message": message}))


class DeleteQuestion(LoginRequiredMixin, View):
    def get(self, request):
        bank = get_object_or_404(QuestionBank, uuid=request.GET.get('bank-uid'))
        question_id = request.GET.get('question-uid')
        if bank.type == 'mc':
            question = get_object_or_404(SingleQuestion, uuid=question_id)
            question.status = False
            question.save()
            bank.count -= 1
            bank.save()
        elif bank.type == 'mcs':
            question = get_object_or_404(MultipleQuestion, uuid=question_id)
            question.status = False
            question.save()
            bank.count -= 1
            bank.save()
        elif bank.type == 'tf':
            question = get_object_or_404(JudgeQuestion, uuid=question_id)
            question.status = False
            question.save()
            bank.count -= 1
            bank.save()
        return HttpResponse(json.dumps({"status": 1}))


class SearchQuestion(LoginRequiredMixin, View):
    def get(self, request, slug):
        buuid = slug
        bank = get_object_or_404(QuestionBank, uuid=buuid, status=True)
        search  = request.GET.get('search_key_info')
        if bank.type == 'mc':
            questions = SingleQuestion.objects.filter(bank=bank, status=True, topic__icontains=search)
            return render(request, 'exam/questions.html', {"questions": questions, "bank": bank})
        elif bank.type == 'mcs':
            questions = MultipleQuestion.objects.filter(bank=bank, status=True, topic__icontains=search)
            return render(request, 'exam/questions.html', {"questions": questions, "bank": bank})
        elif bank.type == 'tf':
            questions = JudgeQuestion.objects.filter(bank=bank, status=True, topic__icontains=search)
            return render(request, 'exam/questions.html', {"questions": questions, "bank": bank})



class GetExaminationList(LoginRequiredMixin, View):
    def get(self, request):
        exams = Examination.objects.filter(creator=request.user)
        return render(request, 'exam/exams.html', {"exams": exams})


class DeleteExamination(LoginRequiredMixin, View):
    def get(self, request, exam_uuid):
        exam = get_object_or_404(Examination, uuid=exam_uuid)
        if exam.status == 'editor':
            if exam.type == 'random':
                randoms = exam.exam_random_to.all()
                for random in randoms:
                    random.delete()
            exam.delete()
        return redirect('exam:exams')


class ExamEditor(LoginRequiredMixin, View):
    def get(self, request, exam_uuid):
        # exam_uuid = request.GET.get('slug')
        if exam_uuid:
            exam = get_object_or_404(Examination, uuid=exam_uuid, status='editor')
            return render(request, 'exam/examsadd.html', {"exam": exam})
        else:
            return render(request, 'exam/examsadd.html')

    def post(self, request, exam_uuid):
        # exam_uuid = request.POST.get('slug')
        exam_title = request.POST.get('exam-name')
        exam_type = request.POST.get('exam-type')
        if not exam_title:
            if exam_uuid:
                exam = get_object_or_404(Examination, uuid=exam_uuid)
                return render(request, 'exam/examsadd.html', {"exam": exam})
            else:
                return render(request, 'exam/examsadd.html')
        elif exam_uuid:
            exam = get_object_or_404(Examination, uuid=exam_uuid)
            exam.title = exam_title
            exam.type = exam_type
            exam.save()
        else:
            exam = Examination.objects.create(creator=request.user,
                                              title=exam_title, type=exam_type)
        return redirect('exam:examdesign', exam_uuid=exam.uuid)


class ExamDesign(LoginRequiredMixin, View):
    def get(self, request, exam_uuid):
        if exam_uuid:
            exam = get_object_or_404(Examination, uuid=exam_uuid, status='editor')
            if exam.type == 'random':
                mcbanks = QuestionBank.objects.filter(creator=request.user, type='mc')
                mcsbanks = QuestionBank.objects.filter(creator=request.user, type='mcs')
                tfbanks = QuestionBank.objects.filter(creator=request.user, type='tf')
                return render(request, 'exam/examsdesign.html',
                              {"exam": exam, "mcbanks": mcbanks, "mcsbanks": mcsbanks, "tfbanks": tfbanks})
            elif exam.type == 'static':
                mcquestions = ExaminationStatic.objects.filter(exam=exam, type='mc').order_by('created_time')
                mcsquestions = ExaminationStatic.objects.filter(exam=exam, type='mcs').order_by('created_time')
                tfquestions = ExaminationStatic.objects.filter(exam=exam, type='tf').order_by('created_time')
                return render(request, 'exam/examstatic.html', {"exam": exam, "mcquestions": mcquestions,
                                    "mcsquestions": mcsquestions, "tfquestions": tfquestions})
        else:
            raise Http404


class GetSelectQuestions(LoginRequiredMixin, View):
    def get(self, request):
        bt = request.GET.get('question_type')
        uuid = request.GET.get('uuid')
        exam = get_object_or_404(Examination, uuid=uuid, status='editor')
        question_list = []
        if bt == 'mc':
            bt = '单项选择题'
            questions = SingleQuestion.objects.filter(bank__creator=request.user, bank__status=True, status=True).exclude(
                uuid__in=[str(question.single_question.uuid) for question in
                          ExaminationStatic.objects.filter(exam=exam, type='mc')]).order_by('created_time')
            for question in questions:
                tmp = []
                tmp.append(str(question.uuid))
                tmp.append(bt)
                tmp.append(str(question.bank.name))
                tmp.append(str(question.topic))
                question_list.append(tmp)
        elif bt == 'mcs':
            bt = '多项选择题'
            questions = MultipleQuestion.objects.filter(bank__creator=request.user, bank__status=True, status=True).exclude(
                uuid__in=[str(question.multiple_question.uuid) for question in
                          ExaminationStatic.objects.filter(exam=exam, type='mcs')]).order_by('created_time')
            for question in questions:
                tmp = []
                tmp.append(str(question.uuid))
                tmp.append(bt)
                tmp.append(str(question.bank.name))
                tmp.append(str(question.topic))
                question_list.append(tmp)
        elif bt == 'tf':
            bt = '判断题'
            questions = JudgeQuestion.objects.filter(bank__creator=request.user, bank__status=True, status=True).exclude(
                uuid__in=[str(question.judge_question.uuid) for question in
                          ExaminationStatic.objects.filter(exam=exam, type='tf')]).order_by('created_time')
            for question in questions:
                tmp = []
                tmp.append(str(question.uuid))
                tmp.append(bt)
                tmp.append(str(question.bank.name))
                tmp.append(str(question.topic))
                question_list.append(tmp)
        return HttpResponse(json.dumps({"status": 1, "questions": question_list}))


class SelectQuestionsAjax(LoginRequiredMixin, View):
    def post(self, request):
        bt = request.POST.get('question_type')
        uuid = request.POST.get('uuid')
        exam = get_object_or_404(Examination, uuid=uuid, status='editor')
        uuids = request.POST.getlist('QuestionSelect')
        if bt == 'mc':
            for uuid in uuids:
                ExaminationStatic.objects.create(exam=exam, type='mc',
                                                 single_question=get_object_or_404(SingleQuestion, uuid=uuid))
        elif bt == 'mcs':
            for uuid in uuids:
                ExaminationStatic.objects.create(exam=exam, type='mcs',
                                                 multiple_question=get_object_or_404(MultipleQuestion, uuid=uuid))
        elif bt == 'tf':
            for uuid in uuids:
                ExaminationStatic.objects.create(exam=exam, type='tf',
                                                 judge_question=get_object_or_404(JudgeQuestion, uuid=uuid))
        return HttpResponse(json.dumps({"status": 1}))


class SetStaticQuestionScore(LoginRequiredMixin, View):
    def get(self, request):
        data = request.GET.get('data')
        bt, uuid, quid = data.split("-")
        score = float(request.GET.get('score'))
        exam = get_object_or_404(Examination, uuid=uuid, status='editor')
        es = Examination.objects.none()
        if bt == 'mc':
            es = get_object_or_404(ExaminationStatic, exam=exam, type='mc', single_question__uuid=quid)
        elif bt == 'mcs':
            es = get_object_or_404(ExaminationStatic, exam=exam, type='mcs', multiple_question__uuid=quid)
        elif bt == 'tf':
            es = get_object_or_404(ExaminationStatic, exam=exam, type='tf', judge_question__uuid=quid)
        es.score = score
        es.save()
        return HttpResponse(json.dumps({"status": 1}))


class DeleteStaticQuestion(LoginRequiredMixin, View):
    def get(self, request):
        data = request.GET.get('data')
        bt, uuid, quid = data.split("-")
        exam = get_object_or_404(Examination, uuid=uuid, status='editor')
        if bt == 'mc':
            get_object_or_404(ExaminationStatic, exam=exam, type='mc', single_question__uuid=quid).delete()
        elif bt == 'mcs':
            get_object_or_404(ExaminationStatic, exam=exam, type='mcs', multiple_question__uuid=quid).delete()
        elif bt == 'tf':
            get_object_or_404(ExaminationStatic, exam=exam, type='tf', judge_question__uuid=quid).delete()
        return HttpResponse(json.dumps({"status": 1}))


class AddRandomNodeAjax(LoginRequiredMixin, View):
    def post(self, request):
        exam_uuid = request.POST.get('exam-uuid')
        exam = get_object_or_404(Examination, uuid=exam_uuid)
        banks = QuestionBank.objects.filter(creator=request.user, type='mc').order_by("-created_time")
        exam_random = ExaminationRandom.objects.create(exam=exam, bank=banks[0])
        rlist = []
        rlist.append(exam_random.uuid)
        rlist.append(exam_random.bank.uuid)
        rlist.append(exam_random.bank.count)
        blist = []
        for bank in banks:
            dic = {}
            dic['uuid'] = bank.uuid
            dic['name'] = bank.name
            blist.append(dic)
        return HttpResponse(json.dumps({"banks": blist, "exam": rlist}))


class QuestionTypeChange(LoginRequiredMixin, View):
    def get(self, request):
        ruuid = request.GET.get('ruuid')
        bank_type = request.GET.get('bank-type')
        exam_random = get_object_or_404(ExaminationRandom, uuid=ruuid)
        status = 1
        message = ""
        blist = []
        banks = QuestionBank.objects.none()
        count = 0
        if bank_type == 'mc':
            banks = QuestionBank.objects.filter(creator=request.user, type='mc').order_by("-created_time")
        elif bank_type == 'mcs':
            banks = QuestionBank.objects.filter(creator=request.user, type='mcs').order_by("-created_time")
        elif bank_type == 'tf':
            banks = QuestionBank.objects.filter(creator=request.user, type='tf').order_by("-created_time")
        if banks:
            exam_random.bank = banks[0]
            exam_random.count = 0
            exam_random.score = 0
            exam_random.save()
            count = banks[0].count
            for bank in banks:
                dic = {}
                dic['uuid'] = bank.uuid
                dic['name'] = bank.name
                blist.append(dic)
        else:
            status = 0
            message = "选择的试题类型中没有题库，请先增加题库"
        return HttpResponse(json.dumps({ "status": status, "message": message, "bank-type": bank_type, "banks": blist, "count": count}))


class QuestionBankChange(LoginRequiredMixin, View):
    def get(self, request):
        bank_uuid = request.GET.get('bank-uuid')
        r_uuid = request.GET.get('ruuid')
        bank = get_object_or_404(QuestionBank, uuid=bank_uuid)
        exam_random = get_object_or_404(ExaminationRandom, uuid = r_uuid)
        exam_random.bank = bank
        exam_random.count = 0
        exam_random.score = 0
        exam_random.save()
        return HttpResponse(json.dumps({"status": 1, "count": bank.count}))


class QuestionNumberSet(LoginRequiredMixin, View):
    def get(self, request):
        r_uuid = request.GET.get('ruuid')
        count = request.GET.get('count')
        exam_random = get_object_or_404(ExaminationRandom, uuid=r_uuid)
        exam_random.count = count
        exam_random.save()
        return HttpResponse(json.dumps({"status": 1, "message": "抽题数量修改成功"}))


class QuestionScoreSet(LoginRequiredMixin, View):
    def get(self, request):
        r_uuid = request.GET.get('ruuid')
        score = request.GET.get('score')
        exam_random = get_object_or_404(ExaminationRandom, uuid=r_uuid)
        exam_random.score = score
        exam_random.save()
        return HttpResponse(json.dumps({"status": 1, "message": "单题分数修改成功"}))


class DeleteRandomNodeAjax(LoginRequiredMixin, View):
    def get(self, request):
        r_uuid = request.GET.get('ruuid')
        exam_random = get_object_or_404(ExaminationRandom, uuid=r_uuid)
        exam_random.delete()
        return HttpResponse(json.dumps({"status": 1, "message": "删除成功"}))


class ExamPublish(LoginRequiredMixin, View):
    def get(self, request, exam_uuid):
        if exam_uuid:
            exam = get_object_or_404(Examination, uuid=exam_uuid, status='editor')
            return render(request, 'exam/examspublish.html', {"exam": exam})
        else:
            raise Http404

    def post(self, request, exam_uuid):
        if exam_uuid:
            exam = get_object_or_404(Examination, uuid=exam_uuid)
            pass_score = request.POST.get('txtPassScore')
            begin_date = request.POST.get('txtBeginDate')
            begin_time = request.POST.get('txtBeginTime')
            try:
                begin = datetime.strptime(begin_date + ' ' + begin_time, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                error_message = "开始时间格式不符合要求，请输入符合格式的数据"
                return HttpResponse(json.dumps({"status": 0, "error": error_message}))
            end_date = request.POST.get('txtEndDate')
            end_time = request.POST.get('txtEndTime')
            try:
                end = datetime.strptime(end_date + ' ' + end_time, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                error_message = "结束时间格式不符合要求，请输入符合格式的数据"
                return HttpResponse(json.dumps({"status": 0, "error": error_message}))
            try:
                if begin > end or end < timezone.now():
                    raise ValueError
            except ValueError:
                error_message = "开始时间大于结束时间或结束时间小于当前时间，数据不符合要求"
                return HttpResponse(json.dumps({"status": 0, "error": error_message}))
            time = request.POST.get('txtExamTime')
            method = request.POST.get('method')
            if method == 'Save':
                try:
                    exam.pass_score = pass_score
                except Exception:
                    error_message = "及格分数数据格式不符合要求，请输入整数"
                    return HttpResponse(json.dumps({"status": 0, "error": error_message}))
                exam.start_time = begin
                exam.end_time = end
                try:
                    exam.time = time
                except Exception:
                    error_message = "答题时间数据格式不符合要求，请输入整数"
                    return HttpResponse(json.dumps({"status": 0, "error": error_message}))
                exam.save()
                return HttpResponse(json.dumps({"status": 1}))
            elif method == 'Publish':
                try:
                    exam.pass_score = pass_score
                except Exception:
                    error_message = "及格分数数据格式不符合要求，请输入整数"
                    return HttpResponse(json.dumps({"status": 0, "error": error_message}))
                exam.start_time = begin
                exam.end_time = end
                try:
                    exam.time = time
                except Exception:
                    error_message = "答题时间数据格式不符合要求，请输入整数"
                    return HttpResponse(json.dumps({"status": 0, "error": error_message}))
                exam.status = 'publish'
                exam.save()
                if exam.type == 'random':
                    exam_randoms = get_list_or_404(ExaminationRandom, exam=exam)
                    mc_banks = []
                    mcs_banks = []
                    tf_banks = []
                    for exam_random in exam_randoms:
                        if exam_random.bank.type == 'mc':
                            dic = {}
                            dic['banks'] = exam_random.bank.bank_to.filter(status=True)
                            dic['num'] = exam_random.count
                            dic['score'] = exam_random.score
                            mc_banks.append(dic)
                        elif exam_random.bank.type == 'mcs':
                            dic = {}
                            dic['banks'] = exam_random.bank.multiple_bank_to.filter(status=True)
                            dic['num'] = exam_random.count
                            dic['score'] = exam_random.score
                            mcs_banks.append(dic)
                        elif exam_random.bank.type == 'tf':
                            dic = {}
                            dic['banks'] = exam_random.bank.judge_bank_to.filter(status=True)
                            dic['num'] = exam_random.count
                            dic['score'] = exam_random.score
                            tf_banks.append(dic)
                    students = get_list_or_404(TeacherStudent, teacher=request.user, status=True)
                    for student in students:
                        examiner = Examiner.objects.create(exam=exam, students=student.student)
                        for question in mc_banks:
                            index = 1
                            max_dict = ExamPaper.objects.filter(examiner=examiner).aggregate(Max('question_num'))
                            if max_dict['question_num__max']:
                                index = max_dict['question_num__max'] + 1
                            storages = random.sample(population=list(question['banks']), k=question['num'])
                            for storage in storages:
                                ExamPaper.objects.create(question_num=index, type='mc', single_question=storage, examiner=examiner, score=question['score'])
                                index += 1
                        for question in mcs_banks:
                            index = 1
                            max_dict = ExamPaper.objects.filter(examiner=examiner).aggregate(Max('question_num'))
                            if max_dict['question_num__max']:
                                index = max_dict['question_num__max'] + 1
                            storages = random.sample(population=list(question['banks']), k=question['num'])
                            for storage in storages:
                                ExamPaper.objects.create(question_num=index, type='mcs', multiple_question=storage, examiner=examiner, score=question['score'])
                                index += 1
                        for question in tf_banks:
                            index = 1
                            max_dict = ExamPaper.objects.filter(examiner=examiner).aggregate(Max('question_num'))
                            if max_dict['question_num__max']:
                                index = max_dict['question_num__max'] + 1
                            storages = random.sample(population=list(question['banks']), k=question['num'])
                            for storage in storages:
                                ExamPaper.objects.create(question_num=index, type='tf', judge_question=storage, examiner=examiner, score=question['score'])
                                index += 1
                elif exam.type == 'static':
                    exam_statics = get_list_or_404(ExaminationStatic, exam=exam)
                    students = get_list_or_404(TeacherStudent, teacher=request.user, status=True)
                    question_num_mcs = exam.get_single_nums() + 1
                    question_num_tf = exam.get_single_nums() + exam.get_multiple_nums() + 1
                    for student in students:
                        mc_num = 1
                        mcs_num = question_num_mcs
                        tf_num = question_num_tf
                        examiner = Examiner.objects.create(exam=exam,
                                                           students=student.student)
                        for exam_static in exam_statics:
                            if exam_static.type == 'mc':
                                ExamPaper.objects.create(question_num=mc_num, type='mc', single_question=exam_static.single_question,
                                                             examiner=examiner, score=exam_static.score)
                                mc_num += 1
                            elif exam_static.type == 'mcs':

                                ExamPaper.objects.create(question_num=mcs_num, type='mcs', multiple_question=exam_static.multiple_question,
                                                         examiner=examiner, score=exam_static.score)
                                mcs_num += 1
                            elif exam_static.type == 'tf':
                                ExamPaper.objects.create(question_num=tf_num, type='tf', judge_question=exam_static.judge_question,
                                                         examiner=examiner, score=exam_static.score)
                                tf_num += 1
            return HttpResponse(json.dumps({"status": 1}))
        else:
            raise Http404


class AllowStudentsVisible(LoginRequiredMixin, View):
    def get(self, request, exam_uuid):
        if exam_uuid:
            exam = get_object_or_404(Examination, uuid=exam_uuid)
            if exam.status == 'publish':
                exam.status = 'view'
                exam.save()
                exam.exam_examiner.update(view=True)
            elif exam.status == 'view':
                exam.status = 'publish'
                exam.save()
                exam.exam_examiner.update(view=False)
            else:
                raise Http404
            return redirect('exam:exams')
        else:
            raise Http404


class GetStudentIndex(LoginRequiredMixin, View):
    def get(self, request):
        examiners = Examiner.objects.filter(students=request.user, has_done=False)
        return render(request, 'exam/candidateexams.html', {"examiners": examiners})


class StartExam(LoginRequiredMixin, View):
    def get(self, request, examiner_uuid):
        examiner = get_object_or_404(Examiner, uuid=examiner_uuid, has_done=False)
        time_now = timezone.now()
        if examiner.exam.start_time < time_now < examiner.exam.end_time and not examiner.has_done and examiner.exam.status is not 'view':
            if examiner.limit_count == 5:
                return render(request, 'exam/limit_out.html')
            if not examiner.do_start_time:
                examiner.do_start_time = time_now
            examiner.do_refresh_time = time_now
            examiner.limit_count += 1
            examiner.save()
            mc_questions = ExamPaper.objects.filter(examiner=examiner, type='mc').order_by('question_num')
            mcs_questions = ExamPaper.objects.filter(examiner=examiner, type='mcs').order_by('question_num')
            tf_questions = ExamPaper.objects.filter(examiner=examiner, type='tf').order_by('question_num')
            return render(request, 'exam/paper.html', {"mcquestions": mc_questions, "mcsquestions": mcs_questions,
                                                       "tfquestions": tf_questions, "examiner": examiner})
        else:
            return redirect("exam:student_index")

    def post(self, request, examiner_uuid):
        examiner = get_object_or_404(Examiner, uuid=examiner_uuid, has_done=False)
        examiner.has_done = True
        examiner.do_submit_time = timezone.now()
        examiner.save()
        answers = []
        for key, _ in request.POST.items():
            dic = {}
            value = "".join(request.POST.getlist(key))
            q_num = key.split("_")[1]
            dic[q_num] = value
            answers.append(dic)
        for dic in answers:
            for q_num, value in dic.items():
                question = examiner.exam_paper.get(question_num=int(q_num))
                question.answer = value
                question.save()
        for question in examiner.exam_paper.all():
            if question.type == 'mc':
                if question.single_question.answer == question.answer:
                    question.is_true = 1
                else:
                    question.is_true = 0
            elif question.type == 'mcs':
                if question.multiple_question.answer == question.answer:
                    question.is_true = 1
                else:
                    question.is_true = 0
            elif question.type == 'tf':
                if question.judge_question.answer == question.answer:
                    question.is_true = 1
                else:
                    question.is_true = 0
            question.save()
        return HttpResponse(json.dumps({"status": 1}))


class GetAllStudentsPaper(LoginRequiredMixin, View):
    def get(self, request, exam_uuid):
        examiners = Examiner.objects.filter(exam__uuid=exam_uuid, has_done=True)
        return render(request, 'exam/exam_historypaper.html', {"examiners": examiners})


class GetHistoryExam(LoginRequiredMixin, View):
    def get(self, request):
        examiners = Examiner.objects.filter(students=request.user, has_done=True, view=True)
        return render(request, 'exam/candidatescore.html', {"examiners": examiners})


class GetHistoryPaper(LoginRequiredMixin, View):
    def get(self, request, examiner_uuid):
        user = request.user
        examiner = Examiner.objects.none()
        if user.role == 'student':
            examiner = get_object_or_404(Examiner, uuid=examiner_uuid, has_done=True, view=True, students=request.user)
        elif user.role == 'teacher':
            examiner = get_object_or_404(Examiner, uuid=examiner_uuid, has_done=True, view=True)
            get_object_or_404(TeacherStudent, teacher=user, student=examiner.students)
        mc_questions = ExamPaper.objects.filter(examiner=examiner, type='mc').order_by('question_num')
        mcs_questions = ExamPaper.objects.filter(examiner=examiner, type='mcs').order_by('question_num')
        tf_questions = ExamPaper.objects.filter(examiner=examiner, type='tf').order_by('question_num')
        return render(request, 'exam/historypaper.html', {"mcquestions": mc_questions, "mcsquestions": mcs_questions,
                                                   "tfquestions": tf_questions, "examiner": examiner})
