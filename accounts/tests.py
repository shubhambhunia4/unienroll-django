from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User

class AccountsModelAndViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.student_user = User.objects.create_user(
            email='student_test@dit.edu',
            password='Password123!',
            first_name='Alex',
            last_name='Student',
            role=User.Role.STUDENT
        )
        self.admin_user = User.objects.create_superuser(
            email='admin_test@dit.edu',
            password='AdminPassword123!',
            first_name='Dean',
            last_name='Admin'
        )

    def test_custom_user_creation_and_roles(self):
        self.assertEqual(self.student_user.role, User.Role.STUDENT)
        self.assertFalse(self.student_user.is_admin)
        self.assertTrue(self.admin_user.is_admin)
        self.assertEqual(self.student_user.get_full_name(), 'Alex Student')

    def test_user_registration_view(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

        post_data = {
            'email': 'new_student@dit.edu',
            'first_name': 'Jordan',
            'last_name': 'Lee',
            'role': User.Role.STUDENT,
            'password': 'NewPassword123!',
            'confirm_password': 'NewPassword123!'
        }
        resp = self.client.post(reverse('register'), post_data)
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(User.objects.filter(email='new_student@dit.edu').exists())

    def test_user_login_logout_flow(self):
        # Successful login
        login_success = self.client.login(email='student_test@dit.edu', password='Password123!')
        self.assertTrue(login_success)

        # Dashboard access
        dashboard_resp = self.client.get(reverse('dashboard'))
        self.assertEqual(dashboard_resp.status_code, 200)

        # Logout
        logout_resp = self.client.get(reverse('logout'))
        self.assertEqual(logout_resp.status_code, 302)

    def test_account_settings_profile_update(self):
        self.client.login(email='student_test@dit.edu', password='Password123!')
        resp = self.client.post(reverse('account_settings'), {
            'action': 'update_profile',
            'first_name': 'Alexander',
            'last_name': 'Student-Updated'
        })
        self.assertEqual(resp.status_code, 302)
        self.student_user.refresh_from_db()
        self.assertEqual(self.student_user.first_name, 'Alexander')
        self.assertEqual(self.student_user.last_name, 'Student-Updated')
