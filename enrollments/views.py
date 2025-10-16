from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Enrollment
from .serializers import EnrollmentSerializer

class EnrollmentListCreateAPI(generics.ListCreateAPIView):
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # 로그인한 회사의 강좌에 등록된 수강 정보만 필터링합니다.
        queryset = Enrollment.objects.filter(course__company=self.request.user)

        # URL의 쿼리 파라미터에서 'course' 값을 가져옵니다.
        course_id = self.request.query_params.get('course', None)

        # 만약 'course' 값이 있다면, 해당 course_id로 추가 필터링합니다.
        if course_id is not None:
            queryset = queryset.filter(course_id=course_id)
            
        return queryset

class EnrollmentDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # 로그인한 회사의 강좌에 등록된 수강 정보만 필터링합니다.
        return Enrollment.objects.filter(course__company=self.request.user)
