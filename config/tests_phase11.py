from django.test import TestCase
from django.core.management import call_command
from accounts.models import User
from academics.models import Department, Course, Semester, Announcement

class Phase11SeedingTestCase(TestCase):
    def test_seed_demo_data_command(self):
        # Execute seed_demo_data management command
        call_command('seed_demo_data')

        # Assert Active Semester created
        active_semester = Semester.objects.filter(is_active=True).first()
        self.assertIsNotNone(active_semester)

        # Assert Departments created
        self.assertGreaterEqual(Department.objects.count(), 5)

        # Assert Courses created
        self.assertGreaterEqual(Course.objects.count(), 8)

        # Assert Admin & Student Accounts created
        self.assertTrue(User.objects.filter(email='admin@dit.edu').exists())
        self.assertTrue(User.objects.filter(email='student@dit.edu').exists())

        # Assert Announcements created
        self.assertGreaterEqual(Announcement.objects.count(), 3)
