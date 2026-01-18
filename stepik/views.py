from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import generics, permissions
from .models import Course
from .serializer import CourseSerializer

class CourseListCreateView(generics.ListCreateAPIView):
    queryset = Course.objects.filter(is_active=True)
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Get list of active courses",
        responses={200: CourseSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create new course",
        request_body=CourseSerializer,
        responses={201: CourseSerializer}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
