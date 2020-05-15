from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import Http404

teacher_url = ['students', 'addStudent', 'searchStudent', 'teacherindex', 'banks', 'addbank', 'deletebank', 'questions',
               'exams', 'exameditor', 'examdesign', 'exampublish', 'examhistorypapers']

student_url = ['studentindex', 'exam_paper', 'historyexam']

anonymous_url = ['/', '/role/get_valid_img']


class FilterUrlMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_anonymous or request.user.is_superuser or request.path in anonymous_url:
            pass
        elif request.user.is_superuser:
            pass
        elif request.path in anonymous_url:
            pass
        elif request.user.role == 'student':
            if request.path.split('/')[2] in teacher_url:
                raise Http404
            else:
                pass
        elif request.user.role == 'teacher':
            if request.path.split('/')[2] in student_url:
                raise Http404
            else:
                pass


