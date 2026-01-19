from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Course
from .serializer import CourseSerializer
from rest_framework.views import APIView


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

class CoursesEditView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Deactivate a course",
        responses={204: 'No Content'}
    )
    def delete(self, request, pk, format=None):
        try:
            course = Course.objects.get(pk=pk, author=request.user)
            course.is_active = False
            course.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Course.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
    @swagger_auto_schema(
        operation_summary="Update a course",
        request_body=CourseSerializer,
        responses={200: CourseSerializer}
    )
    def put(self, request, pk, format=None):
        try:
            course = Course.objects.get(pk=pk, author=request.user)
            serializer = CourseSerializer(course, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Course.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
