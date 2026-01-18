from rest_framework import generics, permissions
from .models import Course, Enrollment, Module, Task, InputOutput, Submission
from .serializer import *

class CourseListCreateView(generics.ListCreateAPIView):
    queryset = Course.objects.filter(is_active=True)
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
