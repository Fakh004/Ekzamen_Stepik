# FILE: stepik/views.py
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Course, Enrollment, Module, Task, InputOutput, Submission
from .serializer import *
from .permissions import IsAdminOrReadOnly, IsInstructorOrAdmin
from .paginations import CoursePagination

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.filter(is_active=True)
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = CoursePagination
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CourseDetailSerializer
        return CourseSerializer
    
    def get_queryset(self):
        queryset = Course.objects.filter(is_active=True)
        
        author_id = self.request.query_params.get('author', None)
        if author_id:
            queryset = queryset.filter(author_id=author_id)
        
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(title__icontains=search)
        
        return queryset

    @swagger_auto_schema(
        operation_summary="Получить список активных курсов",
        manual_parameters=[
            openapi.Parameter('author', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('search', openapi.IN_QUERY, type=openapi.TYPE_STRING),
        ],
        responses={200: CourseSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Получить детали курса",
        responses={200: CourseDetailSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Создать новый курс",
        request_body=CourseSerializer,
        responses={201: CourseSerializer}
    )
    def create(self, request, *args, **kwargs):
        if request.user.role not in ['mentor', 'admin']:
            return Response(
                {'detail': '❌ Только mentor или admin может создавать курсы'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @swagger_auto_schema(
        operation_summary="Обновить курс",
        request_body=CourseSerializer,
        responses={200: CourseSerializer}
    )
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if instance.author != request.user and request.user.role != 'admin':
            return Response(
                {'detail': '❌ У вас нет прав для обновления этого курса'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Удалить курс",
        responses={204: 'No Content'}
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if instance.author != request.user and request.user.role != 'admin':
            return Response(
                {'detail': '❌ У вас нет прав для удаления этого курса'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    @swagger_auto_schema(
        operation_summary="Записаться на курс",
        responses={201: EnrollmentSerializer}
    )
    def enroll(self, request, pk=None):
        course = self.get_object()
        user = request.user
        enrollment, created = Enrollment.objects.get_or_create(user=user, course=course)
        
        if created:
            return Response(
                {
                    'success': True,
                    'message': f'✅ Вы успешно записались на курс "{course.title}"',
                    'enrollment': EnrollmentSerializer(enrollment).data
                },
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'detail': '❌ Вы уже записаны на этот курс'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    @swagger_auto_schema(
        operation_summary="Выписаться из курса",
        responses={204: 'No Content'}
    )
    def unenroll(self, request, pk=None):
        course = self.get_object()
        user = request.user       
        try:
            enrollment = Enrollment.objects.get(user=user, course=course)
            enrollment.delete()
            return Response(
                {'success': True, 'message': f'✅ Вы выписались из курса "{course.title}"'},
                status=status.HTTP_204_NO_CONTENT
            )
        except Enrollment.DoesNotExist:
            return Response(
                {'detail': '❌ Вы не записаны на этот курс'},
                status=status.HTTP_400_BAD_REQUEST
            )


class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.filter(is_active=True)
    serializer_class = ModuleSerializer
    permission_classes = [IsInstructorOrAdmin]

    def get_queryset(self):
        queryset = Module.objects.filter(is_active=True)
        
        course_id = self.request.query_params.get('course', None)
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        
        return queryset

    @swagger_auto_schema(
        operation_summary="Получить список модулей",
        responses={200: ModuleSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        course_id = self.request.data.get('course')
        try:
            course = Course.objects.get(id=course_id)
            
            if course.author != self.request.user and self.request.user.role != 'admin':
                raise ValidationError('❌ У вас нет прав для добавления модулей в этот курс')
            
            serializer.save()
        except Course.DoesNotExist:
            raise ValidationError('❌ Курс не найден')


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsInstructorOrAdmin]

    def get_queryset(self):
        queryset = Task.objects.all()
        
        module_id = self.request.query_params.get('module', None)
        if module_id:
            queryset = queryset.filter(module_id=module_id)
        
        return queryset

    @swagger_auto_schema(
        operation_summary="Получить список заданий",
        responses={200: TaskSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class SubmissionViewSet(viewsets.ModelViewSet):
    serializer_class = SubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CoursePagination

    def get_queryset(self):
        user = self.request.user
        
        if user.role == 'student':
            return Submission.objects.filter(user=user)
        
        if user.role == 'mentor':
            return Submission.objects.filter(task__module__course__author=user)
        return Submission.objects.all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SubmissionDetailSerializer
        return SubmissionSerializer

    @swagger_auto_schema(
        operation_summary="Получить список отправок",
        responses={200: SubmissionSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Отправить решение",
        request_body=SubmissionSerializer,
        responses={201: SubmissionSerializer}
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    @swagger_auto_schema(
        operation_summary="Обновить статус решения (только для mentor/admin)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'status': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=['pending', 'accepted', 'wrong']
                ),
            }
        ),
        responses={200: SubmissionSerializer}
    )
    def update_status(self, request, pk=None):
        submission = self.get_object()
        
        if request.user.role not in ['mentor', 'admin']:
            return Response(
                {'detail': '❌ У вас нет прав для обновления статуса'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        new_status = request.data.get('status')
        if new_status not in ['pending', 'accepted', 'wrong']:
            return Response(
                {'detail': '❌ Неверный статус'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        submission.status = new_status
        submission.save()
        
        return Response(
            {
                'success': True,
                'message': f'✅ Статус обновлен на "{new_status}"',
                'submission': SubmissionSerializer(submission).data
            }
        )

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    @swagger_auto_schema(
        operation_summary="Получить мои решения",
        responses={200: SubmissionSerializer(many=True)}
    )
    def my_submissions(self, request):
        submissions = Submission.objects.filter(user=request.user)
        serializer = self.get_serializer(submissions, many=True)
        return Response(serializer.data)

class EnrollmentListView(generics.ListAPIView):
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Получить мои регистрации",
        responses={200: EnrollmentSerializer(many=True)}
    )
    def get_queryset(self):
        return Enrollment.objects.filter(user=self.request.user)

class UserCourseListView(generics.ListAPIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Получить список курсов, на которые я записан",
        responses={200: CourseSerializer(many=True)}
    )
    def get_queryset(self):
        return Course.objects.filter(
            enrollments__user=self.request.user,
            is_active=True
        ).distinct()