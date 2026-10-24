from django.contrib import admin
from .models import Enrollment, EnrollmentItem

class EnrollmentItemInline(admin.TabularInline):
    model = EnrollmentItem
    extra = 0

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'semester', 'status', 'total_credits', 'total_tuition_fee', 'created_at')
    list_filter = ('status', 'semester')
    search_fields = ('student__email', 'student__first_name', 'student__last_name')
    inlines = [EnrollmentItemInline]

@admin.register(EnrollmentItem)
class EnrollmentItemAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'course', 'enrolled_at')
