# ai/evaluator_cache.py
from .safty_training_ai import MotionEvaluator

# 캐시 키를 (동작이름, 장비종류) 튜플로 사용
evaluator_cache = {}

def get_evaluator(motion_name: str, device_category: str) -> MotionEvaluator:
    """
    캐시에서 평가기를 가져오거나, 없으면 새로 생성하여 캐시에 저장 후 반환하는 함수.
    """
    cache_key = (motion_name, device_category)
    if cache_key in evaluator_cache:
        return evaluator_cache[cache_key]

    # 평가기 생성 시 device_category 전달
    evaluator = MotionEvaluator(motion_name, device_category)
    evaluator_cache[cache_key] = evaluator
    return evaluator

def clear_evaluator_cache(motion_name: str = None, device_category: str = None):
    """
    특정 동작 또는 전체 평가기 캐시를 비움
    """
    global evaluator_cache

    if motion_name and device_category:
        cache_key = (motion_name, device_category)
        if cache_key in evaluator_cache:
            del evaluator_cache[cache_key]
            print(f"'{motion_name}' ({device_category}) 평가기 캐시가 삭제되었습니다.")
    elif motion_name:
        # 해당 동작 이름과 관련된 모든 장비의 캐시 삭제
        keys_to_delete = [key for key in evaluator_cache if key[0] == motion_name]
        for key in keys_to_delete:
            del evaluator_cache[key]
        print(f"'{motion_name}'의 모든 장비 평가기 캐시가 삭제되었습니다.")
    else:
        evaluator_cache = {}
        print("전체 평가기 캐시가 삭제되었습니다.")