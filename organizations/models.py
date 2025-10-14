from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models


class CompanyManager(BaseUserManager):
    """
    커스텀 Company 모델을 위한 매니저 클래스
    """

    def create_user(self, biz_no, name, password=None, **extra_fields):
        if not biz_no:
            raise ValueError("사업자등록번호(biz_no)는 필수 항목입니다.")
        if not name:
            raise ValueError("회사명(name)은 필수 항목입니다.")

        user = self.model(biz_no=biz_no, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, biz_no, name, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser는 is_staff=True 여야 합니다.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser는 is_superuser=True 여야 합니다.")

        return self.create_user(biz_no, name, password, **extra_fields)


class Company(AbstractBaseUser, PermissionsMixin):
    """
    커스텀 인증 유저 모델 (사업자/회사)
    """
    name = models.CharField(max_length=255, verbose_name="회사명")
    biz_no = models.CharField(
        max_length=20, unique=True, verbose_name="사업자등록번호"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    # Django 인증 시스템이 요구하는 필드들
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = CompanyManager()

    # USERNAME_FIELD: 로그인 시 ID로 사용할 필드를 지정
    USERNAME_FIELD = "biz_no"
    # REQUIRED_FIELDS: createsuperuser 커맨드로 관리자 생성 시 입력받을 필드 목록
    REQUIRED_FIELDS = ["name"]

    def __str__(self):
        return f"{self.name} ({self.biz_no})"


class Employee(models.Model):
    """
    회사에 속한 직원 정보
    """

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="employees"
    )
    emp_no = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    dept = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)

    class Meta:
        unique_together = ("company", "emp_no")

    def __str__(self):
        return f"{self.emp_no} - {self.name}"
