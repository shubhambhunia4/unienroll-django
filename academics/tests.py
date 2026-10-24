from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from academics.models import Department, Course, Semester, Announcement

class AcademicsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser(
            email='admin_academic@dit.edu',
            password='AdminPassword123!',
            first_name='Academic',
            last_name='Admin'
        )
        self.student = User.objects.create_user(
            email='student_academic@dit.edu',
            password='Password123!',
            role=User.Role.STUDENT
        )
        self.dept = Department.objects.create(
            name='Computer Science',
            code='CS',
            description='Department of CS'
        )
        self.semester = Semester.objects.create(
            name='Fall 2026',
            code='FALL2026_TEST',
            is_active=True,
            max_credits=18
        )
        self.course = Course.objects.create(
            code='CS101',
            title='Intro to Computer Science',
            description='Foundations of Programming',
            credits=4,
            department=self.dept,
            fee_per_credit=Decimal('1500.00')
        )

    def test_course_fee_calculation(self):
        self.assertEqual(self.course.total_course_fee, Decimal('6000.00'))

    def test_admin_course_creation_and_permission(self):
        # Student forbidden from creating course
        self.client.login(email='student_academic@dit.edu', password='Password123!')
        resp = self.client.get(reverse('admin_course_create'))
        self.assertEqual(resp.status_code, 302)

        # Admin can create course
        self.client.login(email='admin_academic@dit.edu', password='AdminPassword123!')
        post_data = {
            'code': 'CS202',
            'title': 'Data Structures',
            'description': 'Arrays, Trees, Graphs',
            'credits': 4,
            'department': self.dept.id,
            'fee_per_credit': '1500.00'
        }
        resp = self.client.post(reverse('admin_course_create'), post_data)
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Course.objects.filter(code='CS202').exists())

    def test_announcements_creation_and_listing(self):
        announcement = Announcement.objects.create(
            title='Semester Registration Open',
            content='All students can now enroll in fall 2026 courses.',
            category=Announcement.Category.GENERAL,
            created_by=self.admin
        )
        self.client.login(email='student_academic@dit.edu', password='Password123!')
        resp = self.client.get(reverse('announcements_list'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Semester Registration Open')
