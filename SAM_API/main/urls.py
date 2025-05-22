from django.urls import path
from .views import *

urlpatterns = [
    path('teacher-users-stats/', TeacherUsersStatsView.as_view(), name='teacher-users-stats'),
    path('teacher-users-stats/<int:id>/', TeacherEditView.as_view(), name='teacher-users-stats-detail'),
    path('get-excel/', ExportToExcelView.as_view(), name='get-excel'),
    path('topics/', TopicsView.as_view(), name='topics'),
    path('teachers/', TopicedTeachersView.as_view(), name='teachers-list'),

]