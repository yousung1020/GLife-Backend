from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(["GET"])
def company_profile(request):
    """
    프론트 호환용 - 회사 프로필 API (더미 응답)
    실제 구현 시: 세션의 company_id 로 회사 정보 조회
    """
    return Response({
        "id": 1,
        "name": "Demo Company",
        "biz_no": "1234567890",
    })

@api_view(["GET"])
def education_schedule_list(request):
    """
    프론트 호환용 - 교육 일정 목록 API (더미 응답)
    실제 구현 시: Course 모델에서 조회
    """
    return Response([
        {"id": 1, "title": "안전 장비 착용 교육", "quarter": 1},
        {"id": 2, "title": "화재 대피 훈련", "quarter": 2},
    ])
