from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Enrollment
from .serializers import EnrollmentSerializer

class EnrollmentListCreateAPI(generics.ListCreateAPIView):
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # 로그인한 회사의 강좌에 등록된 수강 정보만 필터링합니다.
        return Enrollment.objects.filter(course__company=self.request.user)


class EnrollmentDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # 로그인한 회사의 강좌에 등록된 수강 정보만 필터링합니다.
        return Enrollment.objects.filter(course__company=self.request.user)
