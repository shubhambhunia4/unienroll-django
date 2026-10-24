from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User, Notification
from academics.models import Department, Course, Semester

class Phase8FeaturesTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(
            email='phase8_student@dit.edu',
            password='Password123!',
            first_name='Nova',
            last_name='User'
        )
        self.dept = Department.objects.create(name='Data Science', code='DS')
        self.course = Course.objects.create(
            code='DS101',
            title='Intro to Data Science',
            credits=4,
            department=self.dept,
            schedule_days='Mon / Wed',
            time_slot='10:00 AM - 11:30 AM',
            room_location='Lab B-204',
            max_capacity=60
        )

    def test_notification_creation_and_ordering(self):
        notif1 = Notification.objects.create(
            user=self.student,
            title='Welcome to UniEnroll',
            message='Your student account is active.',
            notification_type=Notification.Type.GENERAL
        )
        notif2 = Notification.objects.create(
            user=self.student,
            title='New Grade Posted',
            message='Grade A assigned for DS101.',
            notification_type=Notification.Type.GRADE
        )

        user_notifications = self.student.notifications.all()
        self.assertEqual(user_notifications.count(), 2)
        self.assertEqual(user_notifications.first(), notif2)  # Most recent first

    def test_api_system_health_endpoint(self):
        response = self.client.get(reverse('api_system_health'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['system_name'], 'UniEnroll ERP Engine')
        self.assertIn('services', data)

    def test_course_schedule_fields(self):
        self.assertEqual(self.course.schedule_days, 'Mon / Wed')
        self.assertEqual(self.course.time_slot, '10:00 AM - 11:30 AM')
        self.assertEqual(self.course.room_location, 'Lab B-204')
        self.assertEqual(self.course.max_capacity, 60)
