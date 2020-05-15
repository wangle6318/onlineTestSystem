from django.urls import path, re_path, include
from exam.views import *

urlpatterns = [
    path('teacherindex', GetTeacherIndex.as_view(), name="index"),
    path('banks', GetQuestionBank.as_view(), name='getbank'),
    path('addbank', AddQuestionBank.as_view(), name='addbank'),
    path('deletebank', DeleteQuestionBank.as_view(), name='deletebank'),
    path('questions', GetQuestions.as_view(), name='getquestion'),
    path('addquestion', AddQuestion.as_view()),
    path('importquestion', BatchAddQuestion.as_view()),
    path('getquestion', GetQuestion.as_view()),
    path('deletetopicimg', DeleteTopicImg.as_view()),
    path('deletequestion', DeleteQuestion.as_view()),
    re_path('searchquestion/(?P<slug>[0-9]{10})', SearchQuestion.as_view(), name='search_question'),
    path('exams', GetExaminationList.as_view(), name='exams'),
    # path('exameditor', ExamEditor.as_view(), name='exameditor'),
    re_path('exameditor/(?P<exam_uuid>[a-z0-9]{0,10})', ExamEditor.as_view(), name='exameditor'),
    re_path('examdesign/(?P<exam_uuid>[a-z0-9]{10})', ExamDesign.as_view(), name='examdesign'),
    path('getSelectQuestions', GetSelectQuestions.as_view()),
    path('selectquestions', SelectQuestionsAjax.as_view()),
    path('setstaticquestionscore', SetStaticQuestionScore.as_view()),
    path('deletestaticquestion', DeleteStaticQuestion.as_view()),
    path('addrandomnode', AddRandomNodeAjax.as_view()),
    path('questiontypechange', QuestionTypeChange.as_view()),
    path('questionbankchange', QuestionBankChange.as_view()),
    path('questionnumberset', QuestionNumberSet.as_view()),
    path('questionscoreset', QuestionScoreSet.as_view()),
    path('deleterandomnode', DeleteRandomNodeAjax.as_view()),
    re_path('exampublish/(?P<exam_uuid>[a-z0-9]{10})', ExamPublish.as_view(), name='examdpublish'),
    re_path('examvisible/(?P<exam_uuid>[a-z0-9]{10})', AllowStudentsVisible.as_view(), name='examvisible'),
    re_path('examdelete/(?P<exam_uuid>[a-z0-9]{10})', DeleteExamination.as_view(), name='examdelete'),
    path('studentindex', GetStudentIndex.as_view(), name='student_index'),
    re_path('exam_paper/(?P<examiner_uuid>[a-z0-9]{10})', StartExam.as_view(), name='exampaper'),
    re_path('examhistorypapers/(?P<exam_uuid>[a-z0-9]{10})', GetAllStudentsPaper.as_view(), name='historypaperlist'),
    path('historyexam', GetHistoryExam.as_view(), name='history'),
    re_path('history_paper/(?P<examiner_uuid>[a-z0-9]{10})', GetHistoryPaper.as_view(), name='historypaper'),
]