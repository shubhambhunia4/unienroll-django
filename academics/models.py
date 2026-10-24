from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Department(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


class Semester(models.Model):
    name = models.CharField(max_length=50)  # e.g., Fall 2026 / Spring 2026
    code = models.CharField(max_length=20, unique=True) # e.g., FALL2026
    is_active = models.BooleanField(default=True)
    max_credits = models.IntegerField(default=24)

    def __str__(self):
        return self.name


class Course(models.Model):
    code = models.CharField(max_length=20, unique=True) # e.g., CS101
    title = models.CharField(max_length=150)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    credits = models.IntegerField(default=4)
    description = models.TextField(blank=True, null=True)
    fee_per_credit = models.DecimalField(max_digits=10, decimal_places=2, default=2500.00)
    
    # Schedule & Capacity (Phase 8)
    schedule_days = models.CharField(max_length=50, default='Mon / Wed')  # e.g., "Mon / Wed" or "Tue / Thu"
    time_slot = models.CharField(max_length=50, default='09:00 AM - 10:30 AM') # e.g., "09:00 AM - 10:30 AM"
    room_location = models.CharField(max_length=100, default='Hall A-101') # e.g., "Tech Building 201"
    max_capacity = models.IntegerField(default=50)

    def __str__(self):
        return f"{self.code} - {self.title} ({self.credits} Credits)"

    @property
    def total_course_fee(self):
        return self.credits * self.fee_per_credit


class Announcement(models.Model):
    class Category(models.TextChoices):
        GENERAL = 'GENERAL', 'General Notice'
        URGENT = 'URGENT', 'Urgent Announcement'
        EXAM = 'EXAM', 'Examinations & Grades'
        FEES = 'FEES', 'Semester Fees & Deadlines'

    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.GENERAL)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.get_category_display()}] {self.title}"
