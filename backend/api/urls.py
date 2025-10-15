from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LoginView, UserViewSet, SubjectViewSet, MarkViewSet,
    StudentReportView, ClassAnalyticsView, StudentAnalyticsView,
    DownloadStudentReportView
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'subjects', SubjectViewSet, basename='subject')
router.register(r'marks', MarkViewSet, basename='mark')

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('student/report/', StudentReportView.as_view(), name='student-report'),
    path('student/report/download/', DownloadStudentReportView.as_view(), name='download-student-report'),
    path('analytics/class/', ClassAnalyticsView.as_view(), name='class-analytics'),
    path('analytics/students/', StudentAnalyticsView.as_view(), name='student-analytics'),
    path('', include(router.urls)),
]