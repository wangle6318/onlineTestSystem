from django.urls import path, re_path, include
from role.views import *

urlpatterns = [
    path('logout', LoginOut.as_view(), name="logout"),
    path('get_valid_img', GetValidImg.as_view(), name='get_valid_img'),
    path('students', GetStudentInfo.as_view(), name='students'),
    path('addStudent', AddStudentInfo.as_view(), name='addStudent'),
    re_path('downloadexcel/(?P<excel_id>[a-z0-9]{1,10})', DownloadExcelTemplate.as_view(), name='downloadexcel'),
    path('uploadstudentfile', BatchAddStudents.as_view()),
    path('searchStudent', SearchStudentInfo.as_view(), name='searchStudent'),
    path('changeStudentStatus', ChangeStudentStatus.as_view()),
    path('editorStudentInfo', EditorStudentInfo.as_view()),
    path('deleteStudentInfo', DeleteStudentInfo.as_view()),
]