# ai/evaluator_cache.py
from .safty_training_ai import MotionEvaluator

evaluator_cache = {}

def get_evaluator(motion_name: str) -> MotionEvaluator:
    """
    캐시에서 평가기를 가져오거나, 없으면 새로 생성하여 캐시에 저장 후 반환하는 함수.
    """
    if motion_name in evaluator_cache:
        return evaluator_cache[motion_name]

    evaluator = MotionEvaluator(motion_name)
    evaluator_cache[motion_name] = evaluator
    return evaluator

def clear_evaluator_cache(motion_name: str = None):
    """
    특정 동작 또는 전체 평가기 캐시를 비움
    """
    global evaluator_cache

    if motion_name:
        if motion_name in evaluator_cache:
            del evaluator_cache[motion_name]
            print(f"'{motion_name}' 평가기 캐시가 삭제되었습니다.")
    else:
        evaluator_cache = {}
        print("전체 평가기 캐시가 삭제되었습니다.")
