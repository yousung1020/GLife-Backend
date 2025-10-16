# ai/serializers.py

from rest_framework import serializers
from .models import UserRecording, MotionRecording, MotionType


class MotionTypeSerializer(serializers.ModelSerializer):
    motionType = serializers.CharField(source='motion_name', max_length=100)

    class Meta:
        model = MotionType
        fields = ['id', 'motionType', 'description', 'max_dtw_distance']
        read_only_fields = ['id', 'max_dtw_distance']


class EvaluationRequestSerializer(serializers.Serializer):
    """Unity로부터 평가 요청을 받을 때의 전체 데이터 형식"""
    motionName = serializers.CharField()
    empNo = serializers.CharField()
    sensorData = serializers.ListField(child=serializers.DictField())


class UserRecordingSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRecording
        fields = ["id", "user", "motion_type", "score", "recorded_at"]
        read_only_fields = ["id", "recorded_at"]


class MotionSerializer(serializers.ModelSerializer):
    motionName = serializers.SlugRelatedField(
        source="motion_type",
        slug_field="motion_name",
        queryset=MotionType.objects.all(),
        write_only=True
    )
    scoreCategory = serializers.CharField(source="score_category")
    sensorData = serializers.JSONField(write_only=True)

    class Meta:
        model = MotionRecording
        fields = [
            "id",
            "motionName",
            "scoreCategory",
            "sensorData",
            "data_frames",
            "recorded_at"
        ]
        read_only_fields = ["id", "data_frames", "recorded_at"]
    
    def create(self, validated_data):
        from .safty_training_ai import preprocess_sensor_data
        raw_sensor_data = validated_data.pop("sensorData")
        preprocessed_numpy = preprocess_sensor_data(raw_sensor_data)
        validated_data["sensor_data_json"] = preprocessed_numpy.tolist()
        validated_data["data_frames"] = preprocessed_numpy.shape[0]
        return super().create(validated_data)