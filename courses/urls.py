from django.urls import path
from .views import CourseListCreateAPI, CourseDetailAPI, BulkEnrollmentView

urlpatterns = [
    path("courses/", CourseListCreateAPI.as_view(), name="course_list_create"),
    path("courses/<int:pk>/", CourseDetailAPI.as_view(), name="course_detail"),
    path("courses/<int:pk>/enroll/", BulkEnrollmentView.as_view(), name="course_bulk_enroll"),
]