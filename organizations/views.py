from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ai.models import MotionType, UserRecording
from .models import Employee, Company
from .serializers import CompanyTokenObtainPairSerializer, EmployeeSerializer
from enrollments.models import Enrollment

class UserRecordingView(APIView):
    def get(self, request, slug, *args, **kwargs):
        motion_type = MotionType.objects.first()
        if not motion_type:
            return Response({"detail": "평가할 MotionType이 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)

        try:
            user_recording = UserRecording.objects.get(user__emp_no=slug, motion_type=motion_type)
            user_status = Enrollment.objects.get(employee__emp_no=slug, course__title="소화기 사용 훈련").status
        except UserRecording.DoesNotExist:
            return Response({"detail": "해당 UserRecording을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        print(user_recording.motion_type.motion_name)

        return Response({
            "ok": True,
            "user": user_recording.user.name,
            "motion_type": user_recording.motion_type.motion_name,
            "score": user_recording.score,
            "recorded_at": user_recording.recorded_at,
            "status": user_status,
        }, status=status.HTTP_200_OK)

class CompanyTokenObtainPairView(APIView):
    def post(self, request, *args, **kwargs):
        print(request.data)
        serializer = CompanyTokenObtainPairSerializer(data=request.data)
        print(serializer.is_valid())
        if serializer.is_valid():
            print("b")
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


class EmployeeViewSet(viewsets.ModelViewSet):
    """
    직원 정보 CRUD 및 대량 등록 API
    """
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated] # 로그인한 회사만 접근 가능

    def get_queryset(self):
        # 로그인한 회사(request.user)에 소속된 직원 정보만 조회
        return Employee.objects.filter(company=self.request.user)

    def perform_create(self, serializer):
        # 직원을 새로 등록할 때, 해당 직원의 소속을 로그인한 회사로 자동 설정
        serializer.save(company=self.request.user)

    @action(detail=False, methods=["post"], url_path="bulk")
    def bulk(self, request):
        """
        직원 정보를 JSON 배열 형태로 받아 대량으로 등록/업데이트합니다.
        POST /api/organizations/employees/bulk/
        """
        
        employees_data = request.data.get("employees", [])
        if not isinstance(employees_data, list):
            return Response(
                {"error": "'employees' 필드는 리스트 형태여야 합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        created_count = 0
        updated_count = 0

        for emp_data in employees_data:
            emp_no = emp_data.get("emp_no")
            if not emp_no:
                continue

            # update_or_create: emp_no가 존재하면 업데이트, 없으면 새로 생성
            obj, created = Employee.objects.update_or_create(
                company=request.user,
                emp_no=emp_no,
                defaults={
                    "name": emp_data.get("name", ""),
                    "dept": emp_data.get("dept", ""),
                    "phone": emp_data.get("phone", ""),
                    "email": emp_data.get("email", ""),
                },
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

            print(updated_count)

        return Response(
            {
                "message": "직원 정보 대량 처리가 완료되었습니다.",
                "created": created_count,
                "updated": updated_count,
            },
            status=status.HTTP_200_OK,
        )
