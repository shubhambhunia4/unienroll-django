from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from academics.models import Department, Course, Semester
from enrollment.models import Enrollment, EnrollmentItem

class EnrollmentTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(
            email='enroll_student@dit.edu',
            password='Password123!',
            first_name='Sam',
            last_name='Enrolled',
            role=User.Role.STUDENT
        )
        self.admin = User.objects.create_superuser(
            email='enroll_admin@dit.edu',
            password='AdminPassword123!',
            first_name='Admin',
            last_name='Enrollment'
        )
        self.dept = Department.objects.create(name='Mathematics', code='MATH')
        self.semester = Semester.objects.create(
            name='Fall 2026',
            code='FALL2026_ENROLL_TEST',
            is_active=True,
            max_credits=18
        )
        self.course1 = Course.objects.create(
            code='MATH101',
            title='Calculus I',
            credits=4,
            department=self.dept,
            fee_per_credit=Decimal('1200.00')
        )

    def test_course_catalog_and_selection(self):
        self.client.login(email='enroll_student@dit.edu', password='Password123!')
        
        # Toggle enrollment for MATH101
        toggle_resp = self.client.post(reverse('toggle_course', args=[self.course1.id]))
        self.assertEqual(toggle_resp.status_code, 302)

        enrollment = Enrollment.objects.get(student=self.student, semester=self.semester)
        self.assertTrue(EnrollmentItem.objects.filter(enrollment=enrollment, course=self.course1).exists())

    def test_credit_limit_enforcement(self):
        big_course = Course.objects.create(
            code='MATH999',
            title='Advanced Super Math',
            credits=20,
            department=self.dept,
            fee_per_credit=Decimal('1000.00')
        )
        self.client.login(email='enroll_student@dit.edu', password='Password123!')
        resp = self.client.post(reverse('toggle_course', args=[big_course.id]))
        self.assertEqual(resp.status_code, 302)

        enrollment = Enrollment.objects.get(student=self.student, semester=self.semester)
        self.assertFalse(EnrollmentItem.objects.filter(enrollment=enrollment, course=big_course).exists())
