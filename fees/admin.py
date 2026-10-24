from django.contrib import admin
from .models import SemesterFee

@admin.register(SemesterFee)
class SemesterFeeAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'tuition_fee', 'exam_fee', 'library_fee', 'infrastructure_fee', 'total_fee', 'is_paid')
    list_filter = ('is_paid',)
