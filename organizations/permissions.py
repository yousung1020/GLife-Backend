from rest_framework.permissions import BasePermission

class IsCompanySession(BasePermission):
    """
    ✅ JWT 인증된 Company만 접근 가능하게 하는 권한 클래스
    """

    def has_permission(self, request, view):
        # request.user 가 인증된 Company 인지 확인
        user = getattr(request, "user", None)
        print(user.is_authenticated)
        if user and user.is_authenticated:
            return True
        return False
