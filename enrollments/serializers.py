from rest_framework import serializers
from .models import Enrollment

class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = "__all__"


class BulkEnrollmentSerializer(serializers.Serializer):
    """
    대량 수강 등록 요청을 검증하기 위한 Serializer
    """
    employee_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False,
        help_text="수강 등록할 직원들의 ID 목록"
    )
    status = serializers.CharField(
        required=False,
        default="enrolled",
        help_text="일괄 적용할 수강 상태"
    )