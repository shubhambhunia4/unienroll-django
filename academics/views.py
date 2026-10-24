from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course, Department, Announcement, Semester
from .forms import CourseForm
from accounts.models import User, Notification
from enrollment.models import Enrollment, EnrollmentItem

@login_required
def admin_course_list_view(request):
    if not request.user.is_admin:
        messages.error(request, "Access restricted to Administrators.")
        return redirect('course_catalog')

    courses = Course.objects.select_related('department').all().order_by('code')
    context = {
        'courses': courses,
        'total_courses_count': courses.count()
    }
    return render(request, 'academics/admin_course_list.html', context)


@login_required
def admin_course_create_view(request):
    if not request.user.is_admin:
        messages.error(request, "Access restricted to Administrators.")
        return redirect('course_catalog')

    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save()
            messages.success(request, f"Successfully created course '{course.code} - {course.title}' ({course.credits} Credits, ₹{course.total_course_fee:,.2f})!")
            return redirect('admin_course_list')
        else:
            messages.error(request, "Please correct the errors in the course form below.")
    else:
        form = CourseForm()

    return render(request, 'academics/admin_course_form.html', {'form': form, 'title': 'Add New Academic Course'})


@login_required
def admin_course_edit_view(request, course_id):
    if not request.user.is_admin:
        messages.error(request, "Access restricted to Administrators.")
        return redirect('course_catalog')

    course = get_object_or_404(Course, pk=course_id)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            course = form.save()
            messages.success(request, f"Updated course '{course.code} - {course.title}' details!")
            return redirect('admin_course_list')
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = CourseForm(instance=course)

    return render(request, 'academics/admin_course_form.html', {'form': form, 'course': course, 'title': f"Edit Course: {course.code}"})


@login_required
def admin_course_delete_view(request, course_id):
    if not request.user.is_admin:
        messages.error(request, "Access restricted to Administrators.")
        return redirect('course_catalog')

    course = get_object_or_404(Course, pk=course_id)
    if request.method == 'POST':
        code = course.code
        title = course.title
        course.delete()
        messages.success(request, f"Dropped and deleted course '{code} - {title}' from academic catalog.")
        return redirect('admin_course_list')

    return render(request, 'academics/admin_course_confirm_delete.html', {'course': course})


# --- Phase 4 Announcements Notice Board ---

@login_required
def announcements_list_view(request):
    announcements = Announcement.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'academics/announcements.html', {
        'announcements': announcements,
        'is_admin_user': request.user.is_admin
    })


@login_required
def announcement_create_view(request):
    if not request.user.is_admin:
        messages.error(request, "Access restricted to Administrators.")
        return redirect('announcements_list')

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        category = request.POST.get('category', Announcement.Category.GENERAL)

        if title and content:
            announcement = Announcement.objects.create(
                title=title,
                content=content,
                category=category,
                created_by=request.user
            )
            # Create notifications for all students
            students = User.objects.filter(role=User.Role.STUDENT)
            notifications = [
                Notification(
                    user=s,
                    title=f"New Notice: {title}",
                    message=content[:150] + ('...' if len(content) > 150 else ''),
                    notification_type=Notification.Type.ANNOUNCEMENT
                ) for s in students
            ]
            Notification.objects.bulk_create(notifications)

            messages.success(request, f"Published university announcement: '{title}'!")
            return redirect('announcements_list')
        else:
            messages.error(request, "Please fill out both title and announcement content.")

    return render(request, 'academics/announcement_form.html')


# --- Phase 4 Admin Grade Roster ---

@login_required
def admin_grade_roster_view(request):
    if not request.user.is_admin:
        messages.error(request, "Access restricted to Administrators.")
        return redirect('dashboard')

    semester = Semester.objects.filter(is_active=True).first()
    enrolled_items = EnrollmentItem.objects.filter(
        enrollment__semester=semester,
        enrollment__status=Enrollment.Status.PAID
    ).select_related('enrollment__student', 'course').order_by('enrollment__student__email', 'course__code')

    grade_choices = EnrollmentItem.Grade.choices

    context = {
        'semester': semester,
        'enrolled_items': enrolled_items,
        'grade_choices': grade_choices
    }
    return render(request, 'academics/admin_grade_roster.html', context)


@login_required
def assign_grade_view(request, item_id):
    if not request.user.is_admin or request.method != 'POST':
        return redirect('admin_grade_roster')

    item = get_object_or_404(EnrollmentItem, pk=item_id)
    new_grade = request.POST.get('grade')
    if new_grade in dict(EnrollmentItem.Grade.choices):
        item.grade = new_grade
        item.save()

        # Create notification for student
        Notification.objects.create(
            user=item.enrollment.student,
            title=f"Grade Posted: {item.course.code}",
            message=f"Your grade for '{item.course.title}' has been updated to '{item.get_grade_display()}'.",
            notification_type=Notification.Type.GRADE
        )

        messages.success(request, f"Assigned Grade '{item.get_grade_display()}' to {item.enrollment.student.get_full_name()} for {item.course.code}.")

    return redirect('admin_grade_roster')
