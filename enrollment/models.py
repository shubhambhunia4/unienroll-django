from django.db import models
from django.conf import settings
from academics.models import Semester, Course

class Enrollment(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft / Cart'
        REGISTERED = 'REGISTERED', 'Pending Payment'
        PAID = 'PAID', 'Confirmed & Paid'

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='enrollments')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'semester')

    def __str__(self):
        return f"{self.student.email} - {self.semester.name} ({self.get_status_display()})"

    @property
    def total_credits(self):
        return sum(item.course.credits for item in self.items.all())

    @property
    def total_tuition_fee(self):
        return sum(item.course.total_course_fee for item in self.items.all())
    
    @property
    def is_paid(self):
        return self.status == self.Status.PAID


class EnrollmentItem(models.Model):
    class Grade(models.TextChoices):
        A_PLUS = 'A+', 'A+ (Outstanding)'
        A = 'A', 'A (Excellent)'
        B_PLUS = 'B+', 'B+ (Very Good)'
        B = 'B', 'B (Good)'
        C = 'C', 'C (Satisfactory)'
        PASS = 'P', 'P (Pass)'
        PENDING = 'PENDING', 'Pending Assessment'

    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='items')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrolled_items')
    grade = models.CharField(max_length=10, choices=Grade.choices, default=Grade.PENDING)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('enrollment', 'course')

    def __str__(self):
        return f"{self.enrollment.student.email} -> {self.course.code} ({self.grade})"
