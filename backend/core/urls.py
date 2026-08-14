from django.urls import path
from core.views import SubjectListView, CourseListView

app_name = 'core'

urlpatterns = [
    path('subjects/', SubjectListView.as_view(), name='subject-list'),
    path('courses/', CourseListView.as_view(), name='course-list'),
]
