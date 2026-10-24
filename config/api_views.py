import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.utils import timezone
from academics.models import Course, Semester
from enrollment.models import Enrollment, EnrollmentItem
from payments.models import Payment
from payments.mongo_logger import MONGO_AVAILABLE
from django.conf import settings
from decimal import Decimal

@require_http_methods(["GET"])
def api_system_health(request):
    """Public health check endpoint inspecting DB and MongoDB status."""
    db_ok = True
    try:
        connection.ensure_connection()
    except Exception:
        db_ok = False

    mongo_status = "Disconnected"
    if MONGO_AVAILABLE:
        try:
            from pymongo import MongoClient
            client = MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=1000)
            client.admin.command('ping')
            mongo_status = "Healthy / Connected"
        except Exception:
            mongo_status = "Warning (Offline/Timeout)"

    return JsonResponse({
        'status': 'healthy' if db_ok else 'unhealthy',
        'system_name': 'UniEnroll ERP Engine',
        'environment': 'Production / Demo',
        'timestamp': timezone.now().isoformat(),
        'services': {
            'relational_database': 'OK' if db_ok else 'ERROR',
            'mongodb_audit_logger': mongo_status
        }
    })


@require_http_methods(["GET"])
def api_courses_list(request):
    """Public/Authenticated API endpoint listing active courses."""
    courses = Course.objects.select_related('department').all().order_by('code')
    data = []
    for c in courses:
        data.append({
            'id': c.id,
            'code': c.code,
            'title': c.title,
            'department': c.department.code,
            'department_name': c.department.name,
            'credits': c.credits,
            'fee_per_credit': float(c.fee_per_credit),
            'total_course_fee': float(c.total_course_fee),
            'schedule_days': c.schedule_days,
            'time_slot': c.time_slot,
            'room_location': c.room_location,
            'max_capacity': c.max_capacity,
            'description': c.description or ''
        })
    return JsonResponse({'status': 'success', 'count': len(data), 'courses': data})


@login_required
@require_http_methods(["GET"])
def api_student_transcript(request):
    """Authenticated endpoint returning student transcript details."""
    semester = Semester.objects.filter(is_active=True).first()
    if not semester:
        return JsonResponse({'status': 'error', 'message': 'No active semester found.'}, status=404)

    enrollment = Enrollment.objects.filter(student=request.user, semester=semester).first()
    if not enrollment:
        return JsonResponse({'status': 'error', 'message': 'No enrollment record found for active semester.'}, status=404)

    items = []
    for item in enrollment.items.select_related('course').all():
        items.append({
            'course_code': item.course.code,
            'course_title': item.course.title,
            'credits': item.course.credits,
            'schedule': f"{item.course.schedule_days} ({item.course.time_slot})",
            'grade': item.get_grade_display() if item.grade else 'In Progress'
        })

    fee = getattr(enrollment, 'fee_breakdown', None)
    fee_data = {
        'tuition_fee': float(fee.tuition_fee) if fee else 0.0,
        'total_fee': float(fee.total_fee) if fee else 0.0,
        'is_paid': fee.is_paid if fee else False
    }

    return JsonResponse({
        'status': 'success',
        'student': {
            'email': request.user.email,
            'full_name': request.user.get_full_name()
        },
        'semester': semester.name,
        'total_credits': enrollment.total_credits,
        'enrollment_status': enrollment.get_status_display(),
        'enrolled_courses': items,
        'fee_summary': fee_data
    })


@login_required
@require_http_methods(["GET"])
def api_admin_analytics(request):
    """Admin-only endpoint for financial analytics summary."""
    if not request.user.is_admin:
        return JsonResponse({'status': 'error', 'message': 'Admin privileges required.'}, status=403)

    semester = Semester.objects.filter(is_active=True).first()
    successful_payments = Payment.objects.filter(status=Payment.Status.SUCCESS)
    total_revenue = sum(p.amount for p in successful_payments)
    
    paid_enrollments_count = Enrollment.objects.filter(status=Enrollment.Status.PAID).count()

    return JsonResponse({
        'status': 'success',
        'active_semester': semester.name if semester else 'None',
        'metrics': {
            'paid_enrollments_count': paid_enrollments_count,
            'total_revenue_inr': float(total_revenue),
            'total_successful_transactions': successful_payments.count()
        }
    })


@login_required
@require_http_methods(["GET"])
def api_admin_audit_logs(request):
    """Admin-only endpoint listing payment audit logs from MongoDB."""
    if not request.user.is_admin:
        return JsonResponse({'status': 'error', 'message': 'Admin privileges required.'}, status=403)

    logs = []
    if MONGO_AVAILABLE:
        try:
            from pymongo import MongoClient
            client = MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=2000)
            db = client[settings.MONGO_DB_NAME]
            collection = db['payment_audit_logs']

            raw_logs = list(collection.find().sort('timestamp', -1).limit(20))
            for log in raw_logs:
                log['_id'] = str(log.get('_id', ''))
                logs.append(log)
        except Exception as e:
            return JsonResponse({'status': 'warning', 'message': f'MongoDB connection warning: {e}', 'logs': []})

    return JsonResponse({'status': 'success', 'count': len(logs), 'audit_logs': logs})


@login_required
@require_http_methods(["POST", "GET"])
def api_ai_advisor(request):
    """Context-aware AI Academic Advisor Chatbot endpoint."""
    if request.method == "POST":
        try:
            body = json.loads(request.body.decode('utf-8'))
            user_query = body.get('query', '').strip()
        except Exception:
            user_query = request.POST.get('query', '').strip()
    else:
        user_query = request.GET.get('query', '').strip()

    query_lower = user_query.lower()
    semester = Semester.objects.filter(is_active=True).first()
    enrollment = Enrollment.objects.filter(student=request.user, semester=semester).first() if semester else None
    fee = getattr(enrollment, 'fee_breakdown', None) if enrollment else None

    # Contextual Intent Analysis
    if any(k in query_lower for k in ['fee', 'cost', 'pay', 'money', 'balance', 'dues', 'price']):
        if not fee:
            reply = "You currently have no course selection registered for fee calculation. Select courses from the Catalog to calculate fees."
        else:
            status_str = "PAID in full" if fee.is_paid else "PENDING payment"
            reply = (
                f"Your fee breakdown for {semester.name}:\n"
                f"• Tuition Fee: ₹{fee.tuition_fee:,.2f}\n"
                f"• Exam Fee: ₹{fee.exam_fee:,.2f}\n"
                f"• Library Fee: ₹{fee.library_fee:,.2f}\n"
                f"• Infrastructure Fee: ₹{fee.infrastructure_fee:,.2f}\n"
                f"• Total Semester Amount: ₹{fee.total_fee:,.2f} ({status_str})."
            )

    elif any(k in query_lower for k in ['recommend', 'suggest', 'course', 'catalog', 'enroll', 'take']):
        enrolled_ids = set(enrollment.items.values_list('course_id', flat=True)) if enrollment else set()
        available_courses = Course.objects.exclude(id__in=enrolled_ids).order_by('code')[:3]
        
        current_credits = enrollment.total_credits if enrollment else 0
        rem_credits = (semester.max_credits - current_credits) if semester else 18

        rec_list = "\n".join([f"• {c.code} - {c.title} ({c.credits} Credits, Room: {c.room_location})" for c in available_courses])
        reply = (
            f"You are currently enrolled in {current_credits} Credits (Remaining capacity: {rem_credits} Credits out of {semester.max_credits} max).\n\n"
            f"Recommended courses for you:\n{rec_list}"
        )

    elif any(k in query_lower for k in ['schedule', 'time', 'room', 'class', 'where', 'when', 'timetable']):
        if not enrollment or enrollment.items.count() == 0:
            reply = "You have not registered for any classes yet."
        else:
            items = enrollment.items.select_related('course').all()
            schedule_str = "\n".join([f"• {item.course.code}: {item.course.schedule_days} @ {item.course.time_slot} ({item.course.room_location})" for item in items])
            reply = f"Here is your active class schedule:\n{schedule_str}"

    else:
        reply = (
            f"Hello {request.user.first_name or 'Student'}! I am your AI Academic Advisor for DIT.\n"
            "I can assist you with:\n"
            "1. Course Recommendations & Credit Limits\n"
            "2. Semester Fee Statements & Razorpay Payment details\n"
            "3. Weekly Class Schedules & Lecture Room Lookups\n\n"
            "How can I help you today?"
        )

    return JsonResponse({
        'status': 'success',
        'user_query': user_query,
        'advisor_reply': reply,
        'timestamp': timezone.now().isoformat()
    })
