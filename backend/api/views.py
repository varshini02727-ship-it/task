from django.contrib.auth import authenticate
from django.db.models import Avg
from rest_framework import viewsets, views, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from .models import User, Subject, Mark
from .serializers import (
    UserSerializer, SubjectSerializer, MarkSerializer,
    ReportSerializer, StudentAnalyticsSerializer
)
from .permissions import IsAdminUser, IsTeacherUser, IsStudentUser
import logging

logger = logging.getLogger('api')

class LoginView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            logger.warning(f"Failed login attempt: User '{username}' not found.")
            return Response({'error': 'Username not found.'}, status=status.HTTP_404_NOT_FOUND)

        user = authenticate(username=username, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            logger.info(f"User '{username}' logged in successfully.")
            return Response({
                'token': token.key,
                'user': { 'id': user.id, 'username': user.username, 'role': user.role }
            })

        logger.warning(f"Failed login attempt for user '{username}': Incorrect password.")
        return Response({'error': 'Incorrect password.'}, status=status.HTTP_401_UNAUTHORIZED)

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer

    def get_queryset(self):
        queryset = User.objects.all().order_by('username')
        role = self.request.query_params.get('role')
        if role is not None:
            queryset = queryset.filter(role=role)
        return queryset

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            self.permission_classes = [IsAdminUser | IsTeacherUser]
        else:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

class SubjectViewSet(viewsets.ModelViewSet):
    serializer_class = SubjectSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == User.Role.ADMIN:
            return Subject.objects.all().order_by('name')
        elif user.role == User.Role.TEACHER:
            return Subject.objects.filter(teacher=user).order_by('name')
        return Subject.objects.none()

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            self.permission_classes = [IsAdminUser | IsTeacherUser]
        else:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

class MarkViewSet(viewsets.ModelViewSet):
    queryset = Mark.objects.all()
    serializer_class = MarkSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsTeacherUser]
        else:
            self.permission_classes = [IsAdminUser | IsTeacherUser]
        return super().get_permissions()

class StudentReportView(views.APIView):
    permission_classes = [IsStudentUser]

    def get(self, request):
        marks = Mark.objects.filter(student=request.user)
        if not marks.exists():
            return Response({"message": "No marks have been entered for you yet."}, status=status.HTTP_200_OK)

        serializer = ReportSerializer(marks, many=True)
        total_score = sum(mark.score for mark in marks)
        percentage = (total_score / (marks.count() * 100)) * 100 if marks.count() > 0 else 0
        grade_map = {90: 'A', 80: 'B', 70: 'C', 60: 'D'}
        overall_grade = next((g for p, g in grade_map.items() if percentage >= p), 'F')

        return Response({
            'student_name': request.user.get_full_name() or request.user.username,
            'marks': serializer.data,
            'total_score': total_score,
            'percentage': round(percentage, 2),
            'overall_grade': overall_grade
        })

class DownloadStudentReportView(views.APIView):
    permission_classes = [IsStudentUser]

    def get(self, request, *args, **kwargs):
        marks = Mark.objects.filter(student=request.user)
        if not marks.exists():
            return HttpResponse("No marks available.", status=404)

        serializer = ReportSerializer(marks, many=True)
        total_score = sum(mark.score for mark in marks)
        percentage = (total_score / (marks.count() * 100)) * 100 if marks.count() > 0 else 0
        grade_map = {90: 'A', 80: 'B', 70: 'C', 60: 'D'}
        overall_grade = next((g for p, g in grade_map.items() if percentage >= p), 'F')
        
        context = {
            'student_name': request.user.get_full_name() or request.user.username,
            'marks': serializer.data,
            'total_score': total_score,
            'percentage': round(percentage, 2),
            'overall_grade': overall_grade,
        }

        html_string = render_to_string('api/grade_report.html', context)
        pdf_file = HTML(string=html_string).write_pdf()
        
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="grade_report.pdf"'
        return response

class ClassAnalyticsView(views.APIView):
    permission_classes = [IsAdminUser | IsTeacherUser]

    def get(self, request):
        analytics = Subject.objects.annotate(average_score=Avg('mark__score')).values('name', 'average_score')
        return Response(analytics)

class StudentAnalyticsView(views.APIView):
    permission_classes = [IsAdminUser | IsTeacherUser]

    def get(self, request, *args, **kwargs):
        students = User.objects.filter(role=User.Role.STUDENT).annotate(
            average_score=Avg('mark__score')
        ).filter(average_score__isnull=False)
        
        serializer = StudentAnalyticsSerializer(students, many=True)
        return Response(serializer.data)