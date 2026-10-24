from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.db.models import Sum
from .forms import UserRegistrationForm, UserLoginForm
from .models import User
from academics.models import Semester, Course
from enrollment.models import Enrollment
from fees.models import SemesterFee
from payments.models import Payment

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Account created successfully for {user.email}! Please sign in.")
            return redirect('login')
        else:
            messages.error(request, "Registration failed. Please correct the errors below.")
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.get_full_name() or user.email}!")
            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid email or password. Please try again.")
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('home')


@login_required
def dashboard_view(request):
    semester = Semester.objects.filter(is_active=True).first()
    enrollment = Enrollment.objects.filter(student=request.user, semester=semester).first() if semester else None
    fee = getattr(enrollment, 'fee_breakdown', None) if enrollment else None
    latest_payment = enrollment.payments.filter(status='SUCCESS').order_by('-created_at').first() if enrollment else None
    enrolled_items = enrollment.items.select_related('course').all() if enrollment else []

    context = {
        'user': request.user,
        'semester': semester,
        'enrollment': enrollment,
        'fee': fee,
        'latest_payment': latest_payment,
        'enrolled_items': enrolled_items
    }

    # Admin executive metrics
    if request.user.is_admin:
        admin_total_students = User.objects.filter(role=User.Role.STUDENT).count()
        paid_enrollments = Enrollment.objects.filter(status=Enrollment.Status.PAID)
        admin_paid_students = paid_enrollments.values('student').distinct().count()
        admin_total_revenue = Payment.objects.filter(status=Payment.Status.SUCCESS).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        admin_total_courses = Course.objects.count()

        context.update({
            'admin_total_students': admin_total_students,
            'admin_paid_students': admin_paid_students,
            'admin_pending_students': max(0, admin_total_students - admin_paid_students),
            'admin_total_revenue': admin_total_revenue,
            'admin_total_courses': admin_total_courses
        })

    return render(request, 'accounts/dashboard.html', context)


@login_required
def account_settings_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_profile':
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            if first_name and last_name:
                request.user.first_name = first_name
                request.user.last_name = last_name
                request.user.save()
                messages.success(request, "Account profile updated successfully!")
            else:
                messages.error(request, "First and last name cannot be empty.")
            return redirect('account_settings')
            
        elif action == 'change_password':
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Your password was updated successfully!")
                return redirect('account_settings')
            else:
                messages.error(request, "Please correct the password errors below.")
    else:
        password_form = PasswordChangeForm(request.user)

    return render(request, 'accounts/settings.html', {'password_form': password_form})
