from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from academics.models import Department, Course, Semester

class ApiEndpointsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser(
            email='api_admin@dit.edu',
            password='AdminPassword123!'
        )
        self.student = User.objects.create_user(
            email='api_student@dit.edu',
            password='Password123!'
        )
        self.dept = Department.objects.create(name='Computer Science', code='CS')
        self.semester = Semester.objects.create(name='Fall 2026', code='FALL2026_API_TEST', is_active=True)
        self.course = Course.objects.create(
            code='CS101',
            title='Intro to CS',
            credits=4,
            department=self.dept,
            fee_per_credit=Decimal('1500.00')
        )

    def test_api_courses_list(self):
        response = self.client.get(reverse('api_courses_list'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertGreaterEqual(data['count'], 1)
        self.assertEqual(data['courses'][0]['code'], 'CS101')

    def test_api_admin_analytics_permissions(self):
        # Student forbidden (403)
        self.client.login(email='api_student@dit.edu', password='Password123!')
        student_resp = self.client.get(reverse('api_admin_analytics'))
        self.assertEqual(student_resp.status_code, 403)

        # Admin allowed (200)
        self.client.login(email='api_admin@dit.edu', password='AdminPassword123!')
        admin_resp = self.client.get(reverse('api_admin_analytics'))
        self.assertEqual(admin_resp.status_code, 200)
        data = admin_resp.json()
        self.assertEqual(data['status'], 'success')
