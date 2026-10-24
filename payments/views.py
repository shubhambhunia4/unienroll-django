import uuid
import json
import csv
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.conf import settings
from django.http import HttpResponse
from academics.models import Semester, Course, Department
from accounts.models import User, Notification
from enrollment.models import Enrollment, EnrollmentItem
from fees.models import SemesterFee
from .models import Payment
from .mongo_logger import log_payment_event_to_mongo, MONGO_AVAILABLE

@login_required
def initiate_checkout_view(request):
    semester = Semester.objects.filter(is_active=True).first()
    if not semester:
        messages.error(request, "No active academic semester found.")
        return redirect('dashboard')

    enrollment = Enrollment.objects.filter(student=request.user, semester=semester).first()
    if not enrollment or enrollment.items.count() == 0:
        messages.warning(request, "No courses selected for enrollment.")
        return redirect('course_catalog')

    fee, _ = SemesterFee.objects.get_or_create(enrollment=enrollment)
    if fee.is_paid:
        messages.info(request, "Your semester fees are already paid in full.")
        return redirect('fee_summary')

    # Create or retrieve pending Payment record
    payment = Payment.objects.filter(
        user=request.user,
        enrollment=enrollment,
        status=Payment.Status.PENDING
    ).order_by('-created_at').first()

    if not payment:
        payment = Payment.objects.create(
            user=request.user,
            enrollment=enrollment,
            amount=fee.total_fee,
            currency='INR',
            razorpay_order_id=f"order_demo_{uuid.uuid4().hex[:12]}"
        )
    else:
        # Update amount in case course selection changed
        payment.amount = fee.total_fee
        payment.save()

    # Log checkout initiation event to MongoDB
    log_payment_event_to_mongo(
        event_type='CHECKOUT_INITIATED',
        transaction_id=payment.transaction_id,
        student_id=request.user.id,
        amount=payment.amount,
        status='PENDING',
        details={'email': request.user.email, 'courses_count': enrollment.items.count()}
    )

    context = {
        'payment': payment,
        'enrollment': enrollment,
        'fee': fee,
        'razorpay_key_id': 'rzp_test_demo_unienroll2026',
    }
    return render(request, 'payments/checkout.html', context)


@login_required
def process_payment_success(request):
    if request.method == 'POST':
        transaction_id = request.POST.get('transaction_id')
        razorpay_payment_id = request.POST.get('razorpay_payment_id') or f"pay_demo_{uuid.uuid4().hex[:10]}"
        razorpay_order_id = request.POST.get('razorpay_order_id') or f"ord_demo_{uuid.uuid4().hex[:10]}"
        razorpay_signature = request.POST.get('razorpay_signature') or f"sig_demo_{uuid.uuid4().hex[:12]}"

        payment = get_object_or_404(Payment, transaction_id=transaction_id, user=request.user)
        
        # Mark payment as success
        payment.status = Payment.Status.SUCCESS
        payment.razorpay_payment_id = razorpay_payment_id
        payment.razorpay_order_id = razorpay_order_id
        payment.razorpay_signature = razorpay_signature
        payment.save()

        # Update enrollment & fee status
        enrollment = payment.enrollment
        enrollment.status = Enrollment.Status.PAID
        enrollment.save()

        fee = getattr(enrollment, 'fee_breakdown', None)
        if fee:
            fee.is_paid = True
            fee.save()

        # Log completion in MongoDB Compass audit database
        log_payment_event_to_mongo(
            event_type='PAYMENT_SUCCESSFUL',
            transaction_id=payment.transaction_id,
            student_id=request.user.id,
            amount=payment.amount,
            status='SUCCESS',
            details={
                'email': request.user.email,
                'razorpay_payment_id': razorpay_payment_id,
                'enrolled_courses': list(enrollment.items.values_list('course__code', flat=True))
            }
        )

        # Create in-app Notification (Phase 8)
        Notification.objects.create(
            user=request.user,
            title='Payment Successful & Registration Confirmed',
            message=f"Your semester fee payment of ₹{payment.amount:,.2f} (Txn: {payment.transaction_id}) was processed successfully.",
            notification_type=Notification.Type.PAYMENT
        )

        messages.success(request, f"Payment of ₹{payment.amount:,.2f} completed successfully via Razorpay! Course registration confirmed.")
        return redirect('payment_receipt', transaction_id=payment.transaction_id)

    return redirect('fee_summary')


@login_required
def payment_receipt_view(request, transaction_id):
    payment = get_object_or_404(Payment, transaction_id=transaction_id)
    # Check permissions: owner or admin
    if payment.user != request.user and not request.user.is_admin:
        messages.error(request, "Permission denied to view this receipt.")
        return redirect('dashboard')

    enrollment = payment.enrollment
    fee = getattr(enrollment, 'fee_breakdown', None)
    enrolled_items = enrollment.items.select_related('course', 'course__department').all()

    context = {
        'payment': payment,
        'enrollment': enrollment,
        'fee': fee,
        'enrolled_items': enrolled_items
    }
    return render(request, 'payments/receipt.html', context)


@login_required
def payment_history_view(request):
    if request.user.is_admin:
        payments = Payment.objects.select_related('user', 'enrollment').order_by('-created_at')
    else:
        payments = Payment.objects.filter(user=request.user).select_related('enrollment').order_by('-created_at')
    return render(request, 'payments/history.html', {'payments': payments})


# --- Admin Analytics & Financial Reports ---

@login_required
def admin_analytics_dashboard_view(request):
    if not request.user.is_admin:
        messages.error(request, "Access restricted to Administrators.")
        return redirect('dashboard')

    semester = Semester.objects.filter(is_active=True).first()
    total_students = User.objects.filter(role=User.Role.STUDENT).count()
    
    paid_enrollments = Enrollment.objects.filter(status=Enrollment.Status.PAID)
    paid_students_count = paid_enrollments.values('student').distinct().count()
    pending_students_count = max(0, total_students - paid_students_count)
    paid_percentage = (paid_students_count / total_students * 100) if total_students > 0 else 0

    successful_payments = Payment.objects.filter(status=Payment.Status.SUCCESS)
    total_revenue = successful_payments.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')

    # Breakdown calculations
    total_tuition_revenue = sum(e.total_tuition_fee for e in paid_enrollments)
    total_exam_revenue = Decimal(paid_students_count * 1500)
    total_library_revenue = Decimal(paid_students_count * 1000)
    total_infrastructure_revenue = Decimal(paid_students_count * 2500)

    # Department revenue data for Chart.js
    dept_labels = []
    dept_revenue = []
    for d in Department.objects.all():
        dept_labels.append(d.code)
        # Sum revenue for paid courses in department
        paid_items = EnrollmentItem.objects.filter(
            enrollment__status=Enrollment.Status.PAID,
            course__department=d
        ).select_related('course')
        d_rev = sum(item.course.total_course_fee for item in paid_items)
        dept_revenue.append(float(d_rev))

    # Top enrolled courses
    top_courses = Course.objects.annotate(
        enrolled_count=Count('enrolled_items')
    ).order_by('-enrolled_count')[:5]

    top_course_codes = [c.code for c in top_courses]
    top_course_counts = [c.enrolled_count for c in top_courses]

    recent_payments = successful_payments.select_related('user', 'enrollment').order_by('-created_at')[:10]

    context = {
        'semester': semester,
        'total_students': total_students,
        'paid_students_count': paid_students_count,
        'pending_students_count': pending_students_count,
        'paid_percentage': round(paid_percentage, 1),
        'total_revenue': total_revenue,
        'total_tuition_revenue': total_tuition_revenue,
        'total_exam_revenue': total_exam_revenue,
        'total_library_revenue': total_library_revenue,
        'total_infrastructure_revenue': total_infrastructure_revenue,
        'dept_labels_json': json.dumps(dept_labels),
        'dept_revenue_json': json.dumps(dept_revenue),
        'top_course_codes_json': json.dumps(top_course_codes),
        'top_course_counts_json': json.dumps(top_course_counts),
        'top_courses': top_courses,
        'recent_payments': recent_payments,
        'now': timezone.now()
    }
    return render(request, 'payments/admin_analytics.html', context)


@login_required
def admin_financial_report_view(request):
    if not request.user.is_admin:
        messages.error(request, "Access restricted to Administrators.")
        return redirect('dashboard')

    semester = Semester.objects.filter(is_active=True).first()
    paid_enrollments = Enrollment.objects.filter(status=Enrollment.Status.PAID)
    paid_students_count = paid_enrollments.values('student').distinct().count()

    successful_payments = Payment.objects.filter(status=Payment.Status.SUCCESS).select_related('user', 'enrollment')
    total_revenue = successful_payments.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')

    tuition_subtotal = sum(e.total_tuition_fee for e in paid_enrollments)
    exam_subtotal = Decimal(paid_students_count * 1500)
    library_subtotal = Decimal(paid_students_count * 1000)
    infra_subtotal = Decimal(paid_students_count * 2500)

    # Course-wise revenue audit
    courses = Course.objects.annotate(
        paid_count=Count('enrolled_items', filter=Q(enrolled_items__enrollment__status=Enrollment.Status.PAID))
    ).all().order_by('code')

    course_revenue_list = []
    for c in courses:
        rev = c.paid_count * c.total_course_fee
        course_revenue_list.append({
            'course': c,
            'paid_count': c.paid_count,
            'revenue': rev
        })

    context = {
        'financial_year': 'FY 2026-2027',
        'semester': semester,
        'paid_students_count': paid_students_count,
        'total_revenue': total_revenue,
        'tuition_subtotal': tuition_subtotal,
        'exam_subtotal': exam_subtotal,
        'library_subtotal': library_subtotal,
        'infra_subtotal': infra_subtotal,
        'course_revenue_list': course_revenue_list,
        'successful_payments': successful_payments,
        'generated_at': timezone.now()
    }
    return render(request, 'payments/financial_report.html', context)


@login_required
def admin_mongodb_logs_view(request):
    if not request.user.is_admin:
        messages.error(request, "Access restricted to Administrators.")
        return redirect('dashboard')

    audit_logs = []
    mongo_status = "Connected"
    error_msg = None

    if MONGO_AVAILABLE:
        try:
            from pymongo import MongoClient
            client = MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=2000)
            db = client[settings.MONGO_DB_NAME]
            collection = db['payment_audit_logs']

            raw_logs = list(collection.find().sort('timestamp', -1).limit(50))
            for log in raw_logs:
                log['id_str'] = str(log.get('_id', ''))
                log['details_json'] = json.dumps(log.get('details', {}), indent=2)
                audit_logs.append(log)
        except Exception as e:
            mongo_status = "Connection Warning"
            error_msg = f"MongoDB connection warning: {e}"
    else:
        mongo_status = "PyMongo Not Installed"
        error_msg = "PyMongo module is not installed."

    context = {
        'audit_logs': audit_logs,
        'audit_logs_count': len(audit_logs),
        'mongo_status': mongo_status,
        'error_msg': error_msg,
        'mongo_uri': settings.MONGO_URI,
        'mongo_db_name': settings.MONGO_DB_NAME
    }
    return render(request, 'payments/mongodb_logs.html', context)


@login_required
def export_financial_csv_view(request):
    if not request.user.is_admin:
        messages.error(request, "Access restricted to Administrators.")
        return redirect('dashboard')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="financial_report_fy2026_2027.csv"'

    writer = csv.writer(response)
    writer.writerow(['Transaction ID', 'Student Name', 'Student Email', 'Amount (INR)', 'Payment Status', 'Payment Method', 'Razorpay Payment ID', 'Date & Time'])

    payments = Payment.objects.select_related('user', 'enrollment').all().order_by('-created_at')
    for p in payments:
        writer.writerow([
            p.transaction_id,
            p.user.get_full_name(),
            p.user.email,
            f"{p.amount:.2f}",
            p.status,
            p.payment_method,
            p.razorpay_payment_id or 'N/A',
            p.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])

    return response
