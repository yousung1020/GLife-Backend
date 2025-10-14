from django.db import models
from organizations.models import Employee
from courses.models import Course

class Enrollment(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="courses")
    enrolled_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default="enrolled")  # 예: 미수강, 수강중, 수강완료

    def __str__(self):
        return f"{self.employee.name} → {self.course.title} ({self.status})"