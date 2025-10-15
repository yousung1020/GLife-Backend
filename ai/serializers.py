# ai/serializers.py

from rest_framework import serializers
from .models import UserRecording, MotionRecording, MotionType


class MotionTypeSerializer(serializers.ModelSerializer):
    motionType = serializers.CharField(source='motion_name', max_length=100)

    class Meta:
        model = MotionType
        # [수정] max_dtw_distances 필드로 변경
        fields = ['id', 'motionType', 'description', 'max_dtw_distances']
        read_only_fields = ['id', 'max_dtw_distances']


class EvaluationRequestSerializer(serializers.Serializer):
    """Unity로부터 평가 요청을 받을 때의 전체 데이터 형식"""
    motionName = serializers.CharField()
    empNo = serializers.CharField()
    deviceCategory = serializers.CharField() # [추가] 장비 종류 필드
    sensorData = serializers.ListField(child=serializers.DictField())


class UserRecordingSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRecording
        fields = ["id", "user", "motion_type", "score", "device_category", "recorded_at"]
        read_only_fields = ["id", "recorded_at"]


class MotionSerializer(serializers.ModelSerializer):
    motionName = serializers.SlugRelatedField(
        source="motion_type",
        slug_field="motion_name",
        queryset=MotionType.objects.all(),
        write_only=True
    )
    scoreCategory = serializers.CharField(source="score_category")
    deviceCategory = serializers.CharField(source="device_category") # [추가] 장비 종류 필드
    sensorData = serializers.JSONField(write_only=True)

    class Meta:
        model = MotionRecording
        fields = [
            "id",
            "motionName",
            "scoreCategory",
            "deviceCategory",
            "sensorData",
            "data_frames",
            "recorded_at"
        ]
        read_only_fields = ["id", "data_frames", "recorded_at"]
    
    def create(self, validated_data):
        # [주의] 전처리 로직은 잠시 후 수정 예정
        from .safty_training_ai import preprocess_sensor_data
        raw_sensor_data = validated_data.pop("sensorData")
        
        # [수정] 전처리 함수에 device_category 전달
        device_category = validated_data.get('device_category')
        preprocessed_numpy = preprocess_sensor_data(raw_sensor_data, device_category)
        
        validated_data["sensor_data_json"] = preprocessed_numpy.tolist()
        validated_data["data_frames"] = preprocessed_numpy.shape[0]
        return super().create(validated_data)
