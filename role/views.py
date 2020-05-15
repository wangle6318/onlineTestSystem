from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from role.codeimg import ValidCodeImg
from django.views.generic import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from role.MyPaginator import MyPaginator
from role.models import User, TeacherStudent
from django.db import transaction, IntegrityError
from django.db.models import Q
from exam.models import ExcelTemplates
import json
from django.http import FileResponse
from django.utils.http import urlquote
from exam.img_save import SaveImg
from xlrd import open_workbook
from xlwt import Workbook
# Create your views here.


def page_not_found(request, exception, template_name='role/404.html'):
    return render(request, template_name)


class LoginRequiredMixin(object):
    """登录状态校验"""
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)


class LoginOut(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        return redirect("index")


class Index(View):
    def get(self, request):
        if request.user.is_authenticated:
            if request.user.role == 'teacher':
                return redirect("exam:index")
            else:
                return redirect("exam:student_index")
        else:
            err = ""
            return render(request, "role/login.html", {"err":err})

    def post(self, request):
        name = request.POST.get('name')
        password = request.POST.get('password')
        rol = request.POST.get('role')
        code = request.POST.get('code')
        err = ""
        if not name and not password and not code:
            err = "学号/工号、密码、验证码不能为空"
        elif code.upper() != request.session.get('valid_code').upper():
            err = "验证码错误"
        else:
            user = authenticate(request, username=name, password=password)
            if user:
                if user.role == rol:
                    login(request, user)
                    if user.role == 'teacher':
                        return redirect("exam:index")
                    else:
                        return redirect("exam:student_index")
                else:
                    err = "角色选择有误"
            else:
                err = "学号/工号或密码错误"
        return render(request, 'role/login.html',{"err": err})


class GetValidImg(View):

    def get(self, request):
        img = ValidCodeImg(width=80, height=32, code_count=4)
        img_data, valid_code = img.getValidCodeImg()
        request.session['valid_code'] = valid_code
        return HttpResponse(img_data)


class GetStudentInfo(LoginRequiredMixin, View):

    def get(self, request):
        students = TeacherStudent.objects.filter(teacher=request.user)
        context = MyPaginator(students, request, 9).paginator()
        students = context['query']
        pages = context['pages']
        return render(request, 'role/students.html', {"students": students, "pages": pages})


class AddStudentInfo(LoginRequiredMixin, View):

    def get(self, request):
        excel = ExcelTemplates.objects.get(is_static=True, type='st')
        return render(request, 'role/studentadd.html', {"message": "", "excel": excel})

    def post(self, request):
        username = request.POST.get('stuId')
        password = request.POST.get('password')
        cpassword = request.POST.get('cpassword')
        name = request.POST.get('name')
        sex = request.POST.get('sex')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        message = ""
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            if username and password:
                if password == cpassword:
                    teacher = request.user
                    try:
                        with transaction.atomic():
                            student = User.objects.create_user(username=username, password=password, name=name, sex=sex, phone=phone, email=email, role='student')
                            TeacherStudent.objects.create(teacher=teacher, student=student)
                    except IntegrityError:
                        message = "添加失败，请重试"
                    else:
                        message = "添加成功，成功加入 {} 组".format(teacher.name)
                else:
                    message = "添加失败：两次输入的密码不一致"
            else:
                message = "添加失败：学号或密码为空"
        else:
            teacher = request.user
            student = User.objects.get(username=username)
            try:
                TeacherStudent.objects.get(teacher=teacher, student=student)
            except TeacherStudent.DoesNotExist:
                TeacherStudent.objects.create(teacher=teacher, student=student)
                message = "添加成功：该用户已存在，成功加入 {} 组".format(teacher.name)
            else:
                message = "添加失败：该用户在 {} 组中".format(teacher.name)
        excel = ExcelTemplates.objects.get(is_static=True, type='st')
        return render(request, 'role/studentadd.html', {"message": message, "excel": excel})


class DownloadExcelTemplate(LoginRequiredMixin, View):
    def get(self, request, excel_id):
        if excel_id.isdigit():
            filename = 'media/' + str(ExcelTemplates.objects.get(id=excel_id, is_static=False).file)
        else:
            filename = 'media/' + str(get_object_or_404(ExcelTemplates, is_static=True, type=excel_id).file)
        thefilename = filename.split("/")[-1]
        file = open(filename, 'rb')
        response = FileResponse(file)
        response['Content-Disposition'] = 'attachment;filename="%s"' % urlquote(thefilename)
        return response


class BatchAddStudents(LoginRequiredMixin, View):
    def post(self, request):
        file = request.FILES.get('file', None)
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
        for i in range(1, nrows):
            row = sheet.row_values(i)
            username = row[0]
            if type(username) is not str:
                username = str(int(float(username)))
            password = row[1]
            if type(password) is not str:
                password = str(int(float(password)))
            name = row[2]
            sex = row[3]
            if sex == '男':
                sex = 'male'
            elif sex == '女':
                sex = 'female'
            else:
                sex = 'nomale'
            phone = row[4]
            if type(phone) is not str:
                phone = str(int(float(phone)))
            email = row[5]
            try:
                student = User.objects.get(username=username)
            except User.DoesNotExist:
                try:
                    with transaction.atomic():
                        student = User.objects.create_user(username=username, password=password, name=name, sex=sex,
                                                           phone=phone, email=email, role='student')
                        TeacherStudent.objects.create(teacher=request.user, student=student)
                except IntegrityError:
                    row.append("添加失败")
                else:
                    row.append("添加成功，成功加入组")
            else:
                try:
                    TeacherStudent.objects.get(teacher=request.user, student=student)
                except TeacherStudent.DoesNotExist:
                    TeacherStudent.objects.create(teacher=request.user, student=student)
                    row.append("用户已存在，成功加入组")
                else:
                    row.append("用户已在组内，不可重复添加")
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
        excel = ExcelTemplates.objects.create(name='考生信息批量上传模板-结果', type='st', file=path.split("media\\")[-1])
        host = request.get_host()
        address = 'http://' + host + '/role/downloadexcel/' + str(excel.id)
        return HttpResponse(json.dumps({"status": 1, "address": address}))


class SearchStudentInfo(LoginRequiredMixin, View):

    def get(self, request):
        username = request.GET.get('searchid')
        if username is None:
            search_id = ""
        else:
            search_id = username
        name = request.GET.get('searchname')
        if name is None:
            search_name = ""
        else:
            search_name = name
        if username and name:
            students = TeacherStudent.objects.filter(
                Q(student__name__icontains=name) | Q(student__username__icontains=username), teacher=request.user)
        elif username:
            students = TeacherStudent.objects.filter(Q(student__username__icontains=username), teacher=request.user)
        elif name:
            students = TeacherStudent.objects.filter(Q(student__name__icontains=name), teacher=request.user)
        else:
            students = TeacherStudent.objects.filter(id=0)
        context = MyPaginator(students, request, 8).paginator()
        students = context['query']
        pages = context['pages']
        return render(request, 'role/studentsearch.html',
                      {"students": students, "pages": pages, "searchid": search_id, "searchname": search_name})

    def post(self, request):
        username = request.POST.get('search-id')
        username = username.replace(" ", "")
        name = request.POST.get('search-name')
        name = name.replace(" ", "")
        if username and name:
            students = TeacherStudent.objects.filter(Q(student__name__icontains=name)| Q(student__username__icontains=username), teacher=request.user)
        elif username:
            students = TeacherStudent.objects.filter(Q(student__username__icontains=username), teacher=request.user)
        elif name:
            students = TeacherStudent.objects.filter(Q(student__name__icontains=name), teacher=request.user)
        else:
            students = TeacherStudent.objects.filter(id=0)
        context = MyPaginator(students, request, 8).paginator()
        students = context['query']
        pages = context['pages']
        return render(request, 'role/studentsearch.html', {"students": students, "pages": pages, "searchid": username, "searchname": name})


class ChangeStudentStatus(LoginRequiredMixin, View):
    def post(self, request):
        if request.is_ajax():
            sname = request.POST.get('student')
            status = 1
            try:
                student = User.objects.get(username=sname)
                ts = TeacherStudent.objects.get(teacher=request.user, student=student)
                if ts.status:
                    ts.status = False
                else:
                    ts.status = True
                ts.save()
            except:
                status = 0
            return HttpResponse(json.dumps({"status": status}))


class EditorStudentInfo(LoginRequiredMixin, View):
    def post(self, request):
        if request.is_ajax():
            username = request.POST.get('username')
            newname = request.POST.get('newname')
            name = request.POST.get('name')
            sex = request.POST.get('sex')
            phone = request.POST.get('phone')
            email = request.POST.get('email')
            status = 1
            message = ""
            user = User.objects.get(username=username)
            if username == newname:
                user.name = name
                user.sex = sex
                user.phone = phone
                user.email = email
                user.save()
                message = "修改成功"
            else:
                try:
                    User.objects.get(username=newname)
                except User.DoesNotExist:
                    user.username = newname
                    user.name = name
                    user.sex = sex
                    user.phone = phone
                    user.email = email
                    user.save()
                    message = "修改成功"
                else:
                    status = 0
                    message = "修改失败：学号已存在"

            return HttpResponse(json.dumps({"status": status, "message": message}))


class DeleteStudentInfo(LoginRequiredMixin, View):
    def post(self, request):
        username = request.POST.get('username')
        status = 1
        message = "删除成功"
        try:
            student = User.objects.get(username=username)
        except User.DoesNotExist:
            status = 0
            message = "删除失败：当前学号不存在"
        else:
            TeacherStudent.objects.get(teacher=request.user, student=student).delete()
        return HttpResponse(json.dumps({"status": status, "message": message}))
