from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Course, Enrollment, Module, Task, InputOutput, Submission

User = get_user_model()

class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role')

class CourseSerializer(serializers.ModelSerializer):
    author = UserBasicSerializer(read_only=True)
    modules_count = serializers.SerializerMethodField()
    enrollment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = ('id', 'title', 'author', 'created_at', 'is_active', 'modules_count', 'enrollment_count')
        read_only_fields = ('id', 'created_at', 'author')
    
    def get_modules_count(self, obj):
        return obj.modules.count()
    
    def get_enrollment_count(self, obj):
        return obj.enrollments.count()

class EnrollmentSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    course = CourseSerializer(read_only=True)
    
    class Meta:
        model = Enrollment
        fields = ('id', 'user', 'course')
        read_only_fields = ('id', 'user')

class InputOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = InputOutput
        fields = ('id', 'task', 'input', 'output')
        read_only_fields = ('id',)

class TaskSerializer(serializers.ModelSerializer):
    input_outputs = InputOutputSerializer(many=True, read_only=True)
    submission_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = ('id', 'module', 'title', 'order', 'task_text', 'input_outputs', 'submission_count')
        read_only_fields = ('id',)
    
    def get_submission_count(self, obj):
        return obj.submissions.count()

class ModuleSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)
    
    class Meta:
        model = Module
        fields = ('id', 'course', 'title', 'is_active', 'tasks')
        read_only_fields = ('id',)

class SubmissionSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    task_title = serializers.CharField(source='task.title', read_only=True)
    
    class Meta:
        model = Submission
        fields = ('id', 'user', 'task', 'task_title', 'code_student', 'status', 'created_at')
        read_only_fields = ('id', 'user', 'status', 'created_at')

class SubmissionDetailSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    task = TaskSerializer(read_only=True)
    
    class Meta:
        model = Submission
        fields = ('id', 'user', 'task', 'code_student', 'status', 'created_at')
        read_only_fields = ('id', 'user', 'status', 'created_at')

class CourseDetailSerializer(serializers.ModelSerializer):
    author = UserBasicSerializer(read_only=True)
    modules = ModuleSerializer(many=True, read_only=True)
    enrollments = EnrollmentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Course
        fields = ('id', 'title', 'author', 'created_at', 'is_active', 'modules', 'enrollments')
        read_only_fields = ('id', 'created_at', 'author')