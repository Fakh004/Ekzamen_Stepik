# FILE: stepik/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'modules', ModuleViewSet, basename='module')
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'submissions', SubmissionViewSet, basename='submission')

app_name = 'stepik'

urlpatterns = [
    path('', include(router.urls)),
    path('enrollments/', EnrollmentListView.as_view(), name='enrollments-list'),
    path('my-courses/', UserCourseListView.as_view(), name='user-courses-list'),
]

