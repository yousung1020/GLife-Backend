# ai/models.py

from django.db import models
import uuid
import secrets
from organizations.models import Employee

# AI 평가 기준 데이터 모델 ---
class MotionType(models.Model):
    """
    '소화기 들기' 등 동작의 종류를 정의하고, 평가에 필요한 요약 정보를 저장.
    """
    motion_name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    # [수정] 장비별 DTW 거리 기준값을 저장하기 위해 JSONField로 변경
    max_dtw_distances = models.JSONField(default=dict, help_text="장비별 최대 DTW 거리 (예: {'gloves': 123, 'lip_motion': 456})")

    def __str__(self):
        return self.motion_name

class MotionRecording(models.Model):
    """
    모범(reference) 또는 0점(zero_score) 동작의 실제 센서 데이터를 저장하는 데이터 원본 창고
    """
    motion_type = models.ForeignKey(MotionType, on_delete=models.CASCADE, related_name="recordings")
    recorded_at = models.DateTimeField(auto_now_add=True)
    data_frames = models.IntegerField()
    score_category = models.CharField(max_length=20, choices=[("reference", "모범 동작"), ("zero_score", "0점 동작")])
    device_category = models.CharField(max_length=20, choices=[("lip_motion", "립모션"), ("gloves", "장갑")], default='gloves')
    sensor_data_json = models.JSONField()

    def get_sensor_data_to_numpy(self):
        import numpy as np
        import pandas as pd
        if self.sensor_data_json:
            df = pd.DataFrame(self.sensor_data_json)
            return df.values
        return np.array([])

# 사용자 평가 결과 저장 모델
class UserRecording(models.Model):
    """
    사용자의 최종 평가 결과를 기록.
    """
    user = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="motion_recordings")
    motion_type = models.ForeignKey(MotionType, on_delete=models.CASCADE)
    score = models.FloatField()
    # 어떤 장비로 평가했는지 기록
    device_category = models.CharField(max_length=20, choices=[("lip_motion", "립모션"), ("gloves", "장갑")], default='gloves')
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.name} - {self.motion_type.motion_name} ({self.score}) - {self.device_category}"
