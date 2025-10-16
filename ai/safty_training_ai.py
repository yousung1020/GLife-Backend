import numpy as np
from .models import MotionRecording
import pandas as pd
import matplotlib.pyplot as plt
from dtaidistance import dtw_ndim
from scipy.signal import savgol_filter

def preprocess_sensor_data(raw_data_dicts) -> np.ndarray:
    if not raw_data_dicts:
        return np.array([])
    
    df = pd.DataFrame(raw_data_dicts)

    window_length = min(df.shape[0] - (df.shape[0] % 2 == 0), 11)
    if window_length < 3:
        window_length = 3

    smoothed_data = df.apply(lambda col: savgol_filter(col, window_length, 3))

    normalized_data = pd.DataFrame(index=smoothed_data.index, columns=smoothed_data.columns)

    for col in smoothed_data.columns:
        if "flex" in col:
            s_min, s_max = 0, 100
        elif "qw" in col:
            s_min, s_max = -30, 30
        elif "qx" in col:
            s_min, s_max = -30, 30
        elif "qy" in col:
            s_min, s_max = -30, 30
        elif "qz" in col:
            s_min, s_max = -30, 30
        else:
            s_min, s_max = 0, 100
    
        range_sensor = s_max - s_min
        if range_sensor == 0:
            normalized_data[col] = 0
        else:
            normalized_data[col] = (smoothed_data[col] - s_min) / range_sensor
    
    return normalized_data.values


class MotionEvaluator:
    def __init__(self, motion_name: str):
        self.motion_name = motion_name
        self.reference_motions_preprocessed = self._load_reference_motions()
    
    def _load_reference_motions(self):
        reference_records = MotionRecording.objects.filter(
            motion_type__motion_name=self.motion_name,
            score_category="reference"
        )
        return [rec.get_sensor_data_to_numpy() for rec in reference_records]
    
    def _preprocess_user_data(self, user_raw_data):
        return preprocess_sensor_data(user_raw_data)

    def evaluator_user_motion(self, user_raw_data, max_dtw_distance: float):
        preprocessed_user_data = self._preprocess_user_data(user_raw_data)

        if not self.reference_motions_preprocessed:
            return {"error": "모범 동작 데이터가 없습니다."}

        dtw_distances = []
        for ref_data in self.reference_motions_preprocessed:
            try:
                distance = dtw_ndim.distance(preprocessed_user_data, ref_data, window=10)
                dtw_distances.append(distance)
            except Exception as e:
                print(f"DTW 거리 계산 중 오류 발생: {e}")
                continue

        if not dtw_distances:
            return {"error": "모든 모범 동작과 비교 중 오류가 발생하여 dtw 거리를 계산할 수 없습니다."}

        average_dtw_distance = sum(dtw_distances) / len(dtw_distances)

        if max_dtw_distance <= 0:
            return {"error": "max_dtw_distance가 0보다 커야 합니다."}
        
        normalized_distance = min(average_dtw_distance / max_dtw_distance, 1.0)
        accuracy_percentage = max(0, (1 - normalized_distance)) * 100
        accuracy_percentage = min(100, accuracy_percentage)

        return {
            "evaluator_motion_name": self.motion_name,
            "score": accuracy_percentage,
            "avg_dtw_distance": average_dtw_distance,
            "normalized_distance": normalized_distance,
        }