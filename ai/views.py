from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status

# --- Models ---
from organizations.models import Employee
from .models import MotionType

# --- Serializers ---
from .serializers import EvaluationRequestSerializer, MotionSerializer, MotionTypeSerializer

# --- Logic ---
from .logic import run_evaluation, update_max_dtw_for_motion


# --- ViewSets & Views ---

class MotionTypeViewSet(ModelViewSet):
    """
    평가 동작 유형(MotionType)을 관리하는 API
    - GET /api/ai/motion-types/
    - POST /api/ai/motion-types/
    """
    queryset = MotionType.objects.all().order_by('motion_name')
    serializer_class = MotionTypeSerializer
    # permission_classes 제거


class MotionRecordingView(APIView):
    """
    모범 동작(reference) 또는 0점 동작(zero_score) 데이터를 받아
    전처리 후 DB에 저장하고, max_dtw_distance를 업데이트합니다.
    """
    # permission_classes 제거
    def post(self, request, *args, **kwargs):
        serializer = MotionSerializer(data=request.data)
        if serializer.is_valid():
            motion_recording = serializer.save()
            update_max_dtw_for_motion(motion_recording.motion_type)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UnifiedEvaluationView(APIView):
    """
    Unity로부터 센서 데이터를 받아 즉시 평가하고 결과를 반환하는 API
    POST /api/ai/evaluate/
    """
    # permission_classes 제거

    def _try_get_employee(self, emp_no: str):
        try:
            # company 정보 없이 emp_no만으로 조회
            return Employee.objects.get(emp_no=emp_no)
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

        employee = self._try_get_employee(emp_no)
        
        if not employee:
            return Response({"detail": f"해당 사원번호({emp_no})가 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)

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