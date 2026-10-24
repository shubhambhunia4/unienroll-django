from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from academics.models import Department, Course, Semester
from enrollment.models import Enrollment, EnrollmentItem
from fees.models import SemesterFee
from payments.models import Payment

class PaymentsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(
            email='pay_student@dit.edu',
            password='Password123!',
            role=User.Role.STUDENT
        )
        self.admin = User.objects.create_superuser(
            email='pay_admin@dit.edu',
            password='AdminPassword123!',
            role=User.Role.ADMIN
        )
        self.dept = Department.objects.create(name='Chemistry', code='CHEM')
        self.semester = Semester.objects.create(name='Fall 2026', code='FALL2026_PAY_TEST', is_active=True)
        self.course = Course.objects.create(
            code='CHEM101',
            title='General Chemistry',
            credits=4,
            department=self.dept,
            fee_per_credit=Decimal('1000.00')
        )
        self.enrollment = Enrollment.objects.create(student=self.student, semester=self.semester)
        EnrollmentItem.objects.create(enrollment=self.enrollment, course=self.course)
        self.fee = SemesterFee.objects.create(enrollment=self.enrollment)

    def test_initiate_checkout_and_process_success(self):
        self.client.login(email='pay_student@dit.edu', password='Password123!')
        
        # Initiate checkout
        resp = self.client.get(reverse('checkout'))
        self.assertEqual(resp.status_code, 200)

        payment = Payment.objects.filter(user=self.student, enrollment=self.enrollment).first()
        self.assertIsNotNone(payment)
        self.assertEqual(payment.status, Payment.Status.PENDING)

        # Process successful payment POST
        post_data = {
            'transaction_id': payment.transaction_id,
            'razorpay_payment_id': 'pay_test_12345',
            'razorpay_order_id': 'ord_test_12345',
            'razorpay_signature': 'sig_test_12345'
        }
        success_resp = self.client.post(reverse('payment_success'), post_data)
        self.assertEqual(success_resp.status_code, 302)

        payment.refresh_from_db()
        self.assertEqual(payment.status, Payment.Status.SUCCESS)

        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.status, Enrollment.Status.PAID)

    def test_admin_analytics_access(self):
        # Student access denied (redirects)
        self.client.login(email='pay_student@dit.edu', password='Password123!')
        resp = self.client.get(reverse('admin_analytics'))
        self.assertEqual(resp.status_code, 302)

        # Admin access granted
        self.client.login(email='pay_admin@dit.edu', password='AdminPassword123!')
        resp_admin = self.client.get(reverse('admin_analytics'))
        self.assertEqual(resp_admin.status_code, 200)
        self.assertContains(resp_admin, 'Financial & Student Revenue Analytics')
