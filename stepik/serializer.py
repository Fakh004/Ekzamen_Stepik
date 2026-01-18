from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Course, Enrollment, Module, Task, InputOutput, Submission

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ("id", "title", "author", "created_at", "is_active")


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ("id", "user", "course")


class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ("id", "course", "title", "is_active")


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ("id", "module", "title", "order", "task_text")


class InputOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = InputOutput
        fields = ("id", "task", "input", "output")


class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ("id", "user", "task", "code_student", "status", "created_at")
        read_only_fields = ("status", "created_at")
