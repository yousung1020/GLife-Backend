from django.db import models
from organizations.models import Company

class Course(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="courses")
    title = models.CharField(max_length=255)  # 과정명
    description = models.TextField(blank=True, null=True)  # 과정 설명
    year = models.IntegerField(default=1)
    quarter = models.IntegerField(default=1)  # 기본값 1로 설정
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
