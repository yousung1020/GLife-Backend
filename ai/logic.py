# ai/logic.py

from dtaidistance import dtw_ndim
from .evaluator_cache import get_evaluator, clear_evaluator_cache
from .models import MotionType, MotionRecording, UserRecording
from organizations.models import Employee
from courses.models import Course
from enrollments.models import Enrollment
from .serializers import UserRecordingSerializer

def run_evaluation(motion_name: str, employee: Employee, raw_sensor_data: list) -> dict:
    """
    센서 데이터 리스트를 받아 평가를 수행하고 결과를 반환하는 핵심 함수
    """
    try:
        motion_type = MotionType.objects.get(motion_name=motion_name)
    except MotionType.DoesNotExist:
        return {"error": f"'{motion_name}' 동작을 찾을 수 없습니다."}

    try:
        evaluator = get_evaluator(motion_name)

        # [디버깅] 1. 사용되는 max_dtw_distance 값 출력
        print(f"[DEBUG] 사용된 max_dtw_distance: {motion_type.max_dtw_distance}")

        result = evaluator.evaluator_user_motion(raw_sensor_data, motion_type.max_dtw_distance)
        
        # [디버깅] 2. evaluator가 계산한 상세 결과 출력
        print(f"[DEBUG] 평가 결과 상세: {result}")

        if "error" in result:
            return result

        # 동일한 사용자와 동작 유형에 대한 기록이 있으면 점수를 업데이트하고, 없으면 새로 생성합니다.
        UserRecording.objects.update_or_create(
            user=employee,
            motion_type=motion_type,
            defaults={'score': result.get("score")}
        )

        try:
            # 평가된 motion_type과 동일한 제목의 Course를 찾습니다.
            course = Course.objects.get(title="소화기 사용 훈련")
            
            # 해당 직원과 Course에 대한 수강 정보(Enrollment)를 찾아 status를 True로 업데이트합니다.
            Enrollment.objects.filter(employee=employee, course=course).update(status=True)
            print(f"Updated enrollment status for {employee.name} in course '{course.title}'.")

        except Course.DoesNotExist:
            print(f"[Warning] Course with title '{motion_type.motion_name}' not found. Cannot update enrollment status.")
        except Exception as e:
            print(f"[Error] Failed to update enrollment status: {e}")

        return result

    except Exception as e:
        print(f"[Error] Evaluation failed for {motion_name}: {e}")
        return {"error": f"평가 중 오류 발생: {str(e)}"}


def update_max_dtw_for_motion(motion_type: MotionType):
    """
    특정 MotionType에 대해 max_dtw_distance를 재계산하고 저장함.
    """
    reference_recordings = MotionRecording.objects.filter(motion_type=motion_type, score_category="reference")
    zero_score_recordings = MotionRecording.objects.filter(motion_type=motion_type, score_category="zero_score")

    if not reference_recordings.exists() or not zero_score_recordings.exists():
        print("모범 동작 또는 0점 동작 데이터가 부족하여 max_dtw_distance를 계산할 수 없습니다.")
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
        motion_type.max_dtw_distance = new_max_dtw
        motion_type.save()
        print(f"'{motion_type.motion_name}'의 새로운 max_dtw_distance: {new_max_dtw}")

        clear_evaluator_cache(motion_type.motion_name)
    else:
        print("유효한 DTW 거리를 계산하지 못했습니다.")
