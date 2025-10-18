from rest_framework import serializers
from .models import Enrollment
from organizations.models import Employee

# 직원 정보를 간단히 보여줄 Serializer
class SimpleEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'name', 'emp_no', 'dept']

# 단일 수강 정보를 다루는 Serializer
class EnrollmentSerializer(serializers.ModelSerializer):
    employee = SimpleEmployeeSerializer(read_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'employee', 'course', 'status', 'enrolled_at']

# 대량 수강 등록을 위한 Serializer
class BulkEnrollmentSerializer(serializers.Serializer):
    """
    대량 수강 등록 요청을 검증하기 위한 Serializer
    """
    employee_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False,
        help_text="수강 등록할 직원들의 ID 목록"
    )
    status = serializers.BooleanField(
        required=False,
        default=False,
        help_text="일괄 적용할 수강 상태"
    )