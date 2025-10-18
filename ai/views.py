from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status

# --- Models ---
from organizations.models import Employee, Company
from .models import MotionType, UserRecording
from courses.models import Course
# --- Serializers ---
from .serializers import EvaluationRequestSerializer, MotionSerializer, MotionTypeSerializer

# --- Logic ---
from .logic import run_evaluation, update_max_dtw_for_motion


class MotionTypeViewSet(ModelViewSet):
    queryset = MotionType.objects.all().order_by('motion_name')
    serializer_class = MotionTypeSerializer


class MotionRecordingView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = MotionSerializer(data=request.data)
        if serializer.is_valid():
            motion_recording = serializer.save()
            update_max_dtw_for_motion(motion_recording.motion_type)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UnifiedEvaluationView(APIView):
    def _try_get_employee(self, emp_no: str, company: Company):
        try:
            return Employee.objects.get(company=company, emp_no=emp_no)
        except Employee.DoesNotExist:
            return None

    def post(self, request, *args, **kwargs):
        serializer = EvaluationRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        motion_name = validated_data['motionName']
        emp_no = validated_data['empNo']
        readings = validated_data['sensorData']

        company = Company.objects.get(biz_no="0123456789")
        if not company:
            return Response({"error": "데이터베이스에 등록된 회사가 없습니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        employee = self._try_get_employee(emp_no, company)

        if not employee:
            return Response({"detail": f"회사({company.name})에 해당 사원번호({emp_no})가 존재하지 않습니다."})

        evaluation_result = run_evaluation(
            motion_name=motion_name,
            employee=employee,
            raw_sensor_data=readings
        )

        if "error" in evaluation_result:
            return Response(evaluation_result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        response_data = {
            "ok": True,
            "detail": "평가가 완료되었습니다.",
            "evaluation": evaluation_result
        }
        return Response(response_data, status=status.HTTP_200_OK)

class UserRecordingView(APIView):
    def get(self, request, slug, *args, **kwargs):
        try:
            motion_type = MotionType.objects.get(motion_name="화재 대피 훈련")
        except MotionType.DoesNotExist:
            return Response({"detail": "기준이 되는 MotionType('화재 대피 훈련')이 존재하지 않습니다."},
                            status=status.HTTP_404_NOT_FOUND)

        user_recording = UserRecording.objects.filter(user__emp_no=slug, motion_type=motion_type).first()

        if not user_recording:
            return Response({"detail": "해당 사용자의 평가 기록을 찾을 수 없습니다."},
                            status=status.HTTP_404_NOT_FOUND)

        return Response({
            "ok": True,
            "user": user_recording.user.name,
            "motion_type": user_recording.motion_type.motion_name,
            "score": user_recording.score,
            "recorded_at": user_recording.recorded_at,
        }, status=status.HTTP_200_OK)
