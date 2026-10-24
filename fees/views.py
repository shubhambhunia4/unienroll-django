from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from academics.models import Semester
from enrollment.models import Enrollment
from .models import SemesterFee

@login_required
def fee_summary_view(request):
    semester = Semester.objects.filter(is_active=True).first()
    if not semester:
        messages.error(request, "No active academic semester found.")
        return redirect('dashboard')

    enrollment = Enrollment.objects.filter(student=request.user, semester=semester).first()
    if not enrollment or enrollment.items.count() == 0:
        messages.warning(request, "Please select at least one course before viewing your fee statement.")
        return redirect('course_catalog')

    fee, _ = SemesterFee.objects.get_or_create(enrollment=enrollment)

    # Latest payment if any
    latest_payment = enrollment.payments.filter(status='SUCCESS').order_by('-created_at').first()

    context = {
        'semester': semester,
        'enrollment': enrollment,
        'fee': fee,
        'latest_payment': latest_payment,
        'enrolled_items': enrollment.items.select_related('course').all()
    }
    return render(request, 'fees/fee_summary.html', context)
