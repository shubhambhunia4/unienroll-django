from decimal import Decimal
from django.db import models
from enrollment.models import Enrollment

class SemesterFee(models.Model):
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE, related_name='fee_breakdown')
    exam_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('1500.00'))
    library_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('1000.00'))
    infrastructure_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('2500.00'))
    is_paid = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Fee Breakdown for {self.enrollment.student.email} ({self.enrollment.semester.name})"

    @property
    def tuition_fee(self):
        return self.enrollment.total_tuition_fee

    @property
    def total_fee(self):
        return (
            self.tuition_fee +
            Decimal(str(self.exam_fee)) +
            Decimal(str(self.library_fee)) +
            Decimal(str(self.infrastructure_fee))
        )
