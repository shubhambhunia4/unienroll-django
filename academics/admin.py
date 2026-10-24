from django.contrib import admin
from .models import Department, Semester, Course

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('code', 'name')

@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active', 'max_credits')
    list_filter = ('is_active',)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'department', 'credits', 'fee_per_credit', 'total_course_fee')
    list_filter = ('department', 'credits')
    search_fields = ('code', 'title')
