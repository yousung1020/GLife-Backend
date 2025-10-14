# organizations/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import CompanyTokenObtainPairView, EmployeeViewSet

# 라우터 생성
router = DefaultRouter()
# employees/ 경로에 EmployeeViewSet을 등록
# 이 한 줄로 직원의 목록, 상세, 생성, 수정, 삭제 API URL이 모두 자동 생성됩니다.
router.register(r"employees", EmployeeViewSet, basename="employee")

urlpatterns = [
    # JWT 인증 관련 URL
    path("login/", CompanyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # 라우터에 등록된 URL들을 포함
    # GET, POST /api/organizations/employees/
    # GET, PUT, DELETE /api/organizations/employees/<id>/
    # POST /api/organizations/employees/bulk/
    path("", include(router.urls)),
]
