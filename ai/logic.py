# ai/logic.py

from dtaidistance import dtw_ndim
from .evaluator_cache import get_evaluator, clear_evaluator_cache
from .models import MotionType, MotionRecording
from organizations.models import Employee
from .serializers import UserRecordingSerializer

def run_evaluation(motion_name: str, employee: Employee, raw_sensor_data: list, device_category: str) -> dict:
    """
    센서 데이터 리스트를 받아 평가를 수행하고 결과를 반환하는 핵심 함수
    """
    try:
        motion_type = MotionType.objects.get(motion_name=motion_name)
    except MotionType.DoesNotExist:
        return {"error": f"'{motion_name}' 동작을 찾을 수 없습니다."}

    try:
        evaluator = get_evaluator(motion_name, device_category)

        max_dist = motion_type.max_dtw_distances.get(device_category)

        if not max_dist:
            return {"error": f"'{motion_name}' 동작({device_category})의 평가 기준값이 설정되지 않았습니다."}

        result = evaluator.evaluator_user_motion(raw_sensor_data, max_dist)
        
        if "error" in result:
            return result

        recording_data = {
            "user": employee.id,
            "motion_type": motion_type.id,
            "score": result.get("score"),
            "device_category": device_category
        }
        
        serializer = UserRecordingSerializer(data=recording_data)
        if serializer.is_valid():
            serializer.save()
        else:
            print(f"[Critical] 사용자 평가 기록 저장 실패: {serializer.errors}")

        return result

    except Exception as e:
        print(f"[Error] Evaluation failed for {motion_name}: {e}")
        return {"error": f"평가 중 오류 발생: {str(e)}"}

def update_max_dtw_for_motion(motion_type: MotionType, device_category: str):
    """
    특정 MotionType과 device_category에 대해 max_dtw_distance를 재계산하고 저장함.
    """

    reference_recordings = MotionRecording.objects.filter(
        motion_type=motion_type, score_category="reference", device_category=device_category
    )
    zero_score_recordings = MotionRecording.objects.filter(
        motion_type=motion_type, score_category="zero_score", device_category=device_category
    )

    if not reference_recordings.exists() or not zero_score_recordings.exists():
        print(f"{device_category}의 모범 동작 또는 0점 동작 데이터가 부족하여 max_dtw_distance를 계산할 수 없습니다.")
        return

    ref_motions = [rec.get_sensor_data_to_numpy() for rec in reference_recordings]
    zero_motions = [rec.get_sensor_data_to_numpy() for rec in zero_score_recordings]

    max_distances = []
    for ref_motion in ref_motions:
        for zero_motion in zero_motions:
            if ref_motion.size == 0 or zero_motion.size == 0:
                continue
            try:
                distance = dtw_ndim.distance(ref_motion, zero_motion, window=10)
                max_distances.append(distance)
            except Exception as e:
                print(f"DTW 거리 계산 중 오류 발생: {e}")
                continue

    if max_distances:
        new_max_dtw = max(max_distances)
        new_max_dtw *= 1.1
        
        motion_type.max_dtw_distances[device_category] = new_max_dtw
        motion_type.save()

        # print(f"'{motion_type.motion_name}' ({device_category})의 새로운 max_dtw_distance: {new_max_dtw}")

        clear_evaluator_cache(motion_type.motion_name, device_category)
    else:
        print("유효한 DTW 거리를 계산하지 못했습니다.")