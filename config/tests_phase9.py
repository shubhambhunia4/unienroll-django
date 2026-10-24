import json
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from academics.models import Department, Course, Semester
from enrollment.models import Enrollment, EnrollmentItem
from fees.models import SemesterFee

class Phase9AiAdvisorTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(
            email='ai_student@dit.edu',
            password='Password123!',
            first_name='Robo',
            last_name='Student'
        )
        self.dept = Department.objects.create(name='Artificial Intelligence', code='AI')
        self.semester = Semester.objects.create(name='Fall 2026', code='FALL2026_AI_TEST', is_active=True)
        self.course = Course.objects.create(
            code='AI101',
            title='Intro to AI & Machine Learning',
            credits=4,
            department=self.dept,
            fee_per_credit=Decimal('2000.00'),
            schedule_days='Mon / Wed',
            time_slot='11:00 AM - 12:30 PM',
            room_location='AI Lab 301'
        )
        self.enrollment = Enrollment.objects.create(student=self.student, semester=self.semester)
        EnrollmentItem.objects.create(enrollment=self.enrollment, course=self.course)
        self.fee = SemesterFee.objects.create(enrollment=self.enrollment)

    def test_ai_advisor_greeting_response(self):
        self.client.login(email='ai_student@dit.edu', password='Password123!')
        response = self.client.get(reverse('api_ai_advisor'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('AI Academic Advisor', data['advisor_reply'])

    def test_ai_advisor_fee_query(self):
        self.client.login(email='ai_student@dit.edu', password='Password123!')
        response = self.client.post(
            reverse('api_ai_advisor'),
            data=json.dumps({'query': 'How much do I owe in semester fees?'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('fee breakdown', data['advisor_reply'].lower())
        self.assertIn('13,000.00', data['advisor_reply'])  # 8000 tuition + 5000 fixed fees

    def test_ai_advisor_schedule_query(self):
        self.client.login(email='ai_student@dit.edu', password='Password123!')
        response = self.client.post(
            reverse('api_ai_advisor'),
            data=json.dumps({'query': 'Where and when is my AI101 class?'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('AI101', data['advisor_reply'])
        self.assertIn('AI Lab 301', data['advisor_reply'])
