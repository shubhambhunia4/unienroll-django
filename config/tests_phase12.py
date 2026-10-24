from django.test import TestCase, Client
from django.conf import settings

class Phase12SecurityAuditTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_security_headers_configured(self):
        self.assertTrue(getattr(settings, 'SECURE_BROWSER_XSS_FILTER', False))
        self.assertTrue(getattr(settings, 'SECURE_CONTENT_TYPE_NOSNIFF', False))
        self.assertEqual(getattr(settings, 'X_FRAME_OPTIONS', ''), 'DENY')

    def test_xframe_options_header_in_response(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get('X-Frame-Options'), 'DENY')
