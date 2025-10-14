from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Course
from .serializers import CourseSerializer
from organizations.models import Employee
from enrollments.models import Enrollment
from enrollments.serializers import BulkEnrollmentSerializer


class CourseListCreateAPI(generics.ListCreateAPIView):
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # JWT 토큰의 user(Company) 정보를 기반으로 강좌를 필터링합니다.
        return Course.objects.filter(company=self.request.user)

    def perform_create(self, serializer):
        # 강좌 생성 시, 요청한 user(Company) 소속으로 자동 설정합니다.
        serializer.save(company=self.request.user)


class CourseDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # JWT 토큰의 user(Company) 정보를 기반으로 강좌를 필터링합니다.
        return Course.objects.filter(company=self.request.user)


class BulkEnrollmentView(APIView):
    """
    특정 Course에 여러 Employee를 대량으로 수강 등록/수정하는 API
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        # 1. URL에서 pk를 이용해 Course 객체를 가져옵니다.
        try:
            course = Course.objects.get(pk=pk, company=request.user)
        except Course.DoesNotExist:
            return Response({"error": "해당 교육 과정을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        # 2. 요청 데이터를 BulkEnrollmentSerializer로 검증합니다.
        serializer = BulkEnrollmentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        employee_ids = serializer.validated_data['employee_ids']
        enroll_status = serializer.validated_data['status']

        # 3. 요청된 직원 ID들이 실제 존재하고, 현재 로그인한 회사 소속인지 확인합니다.
        employees = Employee.objects.filter(pk__in=employee_ids, company=request.user)
        
        if len(employee_ids) != employees.count():
            return Response({"error": "잘못되었거나 권한이 없는 직원 ID가 포함되어 있습니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 4. 각 직원에 대해 수강 정보를 생성하거나 업데이트합니다.
        created_count = 0
        updated_count = 0
        for employee in employees:
            # update_or_create: 없으면 만들고, 있으면 가져옴
            obj, created = Enrollment.objects.update_or_create(
                course=course,
                employee=employee,
                defaults={'status': enroll_status}
            )
            if created:
                created_count += 1
            else:
                updated_count += 1
        
        # 5. 최종 결과를 응답합니다.
        return Response({
            "message": "대량 수강 신청 처리가 완료되었습니다.",
            "course_title": course.title,
            "created": created_count,
            "updated": updated_count
        }, status=status.HTTP_200_OK)