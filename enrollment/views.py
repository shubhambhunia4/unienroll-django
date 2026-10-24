from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from academics.models import Semester, Course, Department
from accounts.models import User
from .models import Enrollment, EnrollmentItem
from fees.models import SemesterFee

@login_required
def course_catalog_view(request):
    semester = Semester.objects.filter(is_active=True).first()
    if not semester:
        messages.error(request, "No active academic semester found.")
        return redirect('dashboard')

    enrollment, _ = Enrollment.objects.get_or_create(
        student=request.user,
        semester=semester
    )
    
    # Auto-preselect 4 courses if student has 0 courses in cart
    if enrollment.items.count() == 0 and not enrollment.is_paid:
        default_codes = ['CS101', 'CS202', 'CS301', 'MATH101']
        default_courses = Course.objects.filter(code__in=default_codes)
        for c in default_courses:
            EnrollmentItem.objects.get_or_create(enrollment=enrollment, course=c)

    # Ensure SemesterFee object exists
    SemesterFee.objects.get_or_create(enrollment=enrollment)

    enrolled_course_ids = set(enrollment.items.values_list('course_id', flat=True))
    
    # Search and Filter Parameters
    query = request.GET.get('q', '').strip()
    dept_code = request.GET.get('dept', '').strip().upper()

    courses = Course.objects.select_related('department').all()

    if query:
        courses = courses.filter(Q(code__icontains=query) | Q(title__icontains=query) | Q(description__icontains=query))

    if dept_code:
        courses = courses.filter(department__code=dept_code)

    courses = courses.order_by('code')
    departments = Department.objects.all()

    context = {
        'semester': semester,
        'enrollment': enrollment,
        'courses': courses,
        'departments': departments,
        'selected_dept': dept_code,
        'search_query': query,
        'total_courses_count': Course.objects.count(),
        'enrolled_course_ids': enrolled_course_ids,
        'max_credits': semester.max_credits,
        'remaining_credits': semester.max_credits - enrollment.total_credits,
        'is_admin_user': request.user.is_admin
    }
    return render(request, 'enrollment/course_list.html', context)


@login_required
def toggle_course_enrollment(request, course_id):
    if request.method != 'POST':
        return redirect('course_catalog')

    semester = Semester.objects.filter(is_active=True).first()
    if not semester:
        messages.error(request, "No active academic semester found.")
        return redirect('course_catalog')

    # Target student (default current user, or student_id if passed by admin)
    student_id = request.POST.get('student_id')
    if student_id and request.user.is_admin:
        target_student = get_object_or_404(User, pk=student_id)
    else:
        target_student = request.user

    enrollment, _ = Enrollment.objects.get_or_create(
        student=target_student,
        semester=semester
    )

    # Check lock status: If paid and user is NOT admin, block changes
    if enrollment.is_paid and not request.user.is_admin:
        messages.error(
            request,
            "Course registration is locked after fee payment. Only an Administrator can allow course drops or edits."
        )
        return redirect('course_catalog')

    course = get_object_or_404(Course, pk=course_id)
    item = EnrollmentItem.objects.filter(enrollment=enrollment, course=course).first()

    if item:
        item.delete()
        if request.user.is_admin and target_student != request.user:
            messages.success(request, f"Admin Action: Dropped '{course.code}' for student {target_student.email}.")
        else:
            messages.info(request, f"Removed '{course.code} - {course.title}' from your enrollment.")
    else:
        # Check credit limit
        if enrollment.total_credits + course.credits > semester.max_credits:
            messages.error(
                request,
                f"Cannot enroll in {course.code} ({course.credits} Credits). Credit limit of {semester.max_credits} Credits exceeded."
            )
            return redirect('course_catalog')

        EnrollmentItem.objects.create(enrollment=enrollment, course=course)
        messages.success(request, f"Enrolled in '{course.code} - {course.title}'!")

    # Synchronize Fee Breakdown
    fee, _ = SemesterFee.objects.get_or_create(enrollment=enrollment)
    fee.save()

    if student_id and request.user.is_admin:
        return redirect('admin_enrollment_manage')
    return redirect('course_catalog')


@login_required
def academic_transcript_view(request, student_id=None):
    """Generates official printable Academic Registration Transcript for paid students."""
    if student_id and request.user.is_admin:
        student = get_object_or_404(User, pk=student_id)
    else:
        student = request.user

    semester = Semester.objects.filter(is_active=True).first()
    enrollment = Enrollment.objects.filter(student=student, semester=semester).first()

    if not enrollment:
        messages.warning(request, "No active course enrollment found.")
        return redirect('course_catalog')

    if not enrollment.is_paid and not request.user.is_admin:
        messages.warning(request, "Academic Transcript is issued after semester fee payment is completed.")
        return redirect('fee_summary')

    enrolled_items = enrollment.items.select_related('course', 'course__department').all().order_by('course__code')
    fee = getattr(enrollment, 'fee_breakdown', None)
    payment = enrollment.payments.filter(status='SUCCESS').order_by('-created_at').first()

    context = {
        'student': student,
        'semester': semester,
        'enrollment': enrollment,
        'enrolled_items': enrolled_items,
        'fee': fee,
        'payment': payment
    }
    return render(request, 'enrollment/academic_transcript.html', context)


@login_required
def admin_unlock_enrollment(request, enrollment_id):
    if not request.user.is_admin:
        messages.error(request, "Permission denied. Only Administrators can unlock paid enrollments.")
        return redirect('dashboard')

    enrollment = get_object_or_404(Enrollment, pk=enrollment_id)
    enrollment.status = Enrollment.Status.DRAFT
    enrollment.save()
    
    fee = getattr(enrollment, 'fee_breakdown', None)
    if fee:
        fee.is_paid = False
        fee.save()

    messages.success(request, f"Admin Override: Unlocked enrollment for {enrollment.student.email}.")
    return redirect('admin_enrollment_manage')


@login_required
def admin_enrollment_manage_view(request):
    if not request.user.is_admin:
        messages.error(request, "Access restricted to Administrators.")
        return redirect('dashboard')

    semester = Semester.objects.filter(is_active=True).first()
    enrollments = Enrollment.objects.filter(semester=semester).select_related('student', 'fee_breakdown').prefetch_related('items__course').all()

    context = {
        'semester': semester,
        'enrollments': enrollments
    }
    return render(request, 'enrollment/admin_manage.html', context)


@login_required
def my_courses_view(request):
    semester = Semester.objects.filter(is_active=True).first()
    enrollment = Enrollment.objects.filter(student=request.user, semester=semester).first()
    
    enrolled_items = enrollment.items.select_related('course', 'course__department').all() if enrollment else []

    context = {
        'semester': semester,
        'enrollment': enrollment,
        'enrolled_items': enrolled_items
    }
    return render(request, 'enrollment/my_courses.html', context)
