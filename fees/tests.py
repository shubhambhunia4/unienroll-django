from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from academics.models import Department, Course, Semester
from enrollment.models import Enrollment, EnrollmentItem
from fees.models import SemesterFee

class FeesTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(
            email='fees_student@dit.edu',
            password='Password123!',
            role=User.Role.STUDENT
        )
        self.dept = Department.objects.create(name='Physics', code='PHY')
        self.semester = Semester.objects.create(name='Fall 2026', code='FALL2026_FEES_TEST', is_active=True)
        self.course = Course.objects.create(
            code='PHY101',
            title='General Physics I',
            credits=4,
            department=self.dept,
            fee_per_credit=Decimal('1000.00')
        )
        self.enrollment = Enrollment.objects.create(student=self.student, semester=self.semester)
        EnrollmentItem.objects.create(enrollment=self.enrollment, course=self.course)

    def test_fee_breakdown_calculations(self):
        fee = SemesterFee.objects.create(enrollment=self.enrollment)
        # 4 credits * 1000 = 4000 tuition fee
        self.assertEqual(fee.tuition_fee, Decimal('4000.00'))
        # Total = 4000 + 1500 (exam) + 1000 (library) + 2500 (infra) = 9000.00
        self.assertEqual(fee.total_fee, Decimal('9000.00'))

    def test_fee_summary_view(self):
        self.client.login(email='fees_student@dit.edu', password='Password123!')
        response = self.client.get(reverse('fee_summary'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '9000.00')
