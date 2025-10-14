from django.urls import path
from .views import EnrollmentListCreateAPI, EnrollmentDetailAPI

urlpatterns = [
    path("", EnrollmentListCreateAPI.as_view(), name="enrollment_list_create"),
    path("<int:pk>/", EnrollmentDetailAPI.as_view(), name="enrollment_detail"),
]
