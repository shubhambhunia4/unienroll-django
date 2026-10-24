from django.test import TestCase, Client
from django.template.loader import render_to_string

class Phase10PolishTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_404_custom_template_rendering(self):
        response = self.client.get('/invalid-path-non-existent-url-999/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_custom_error_templates_exist(self):
        html_404 = render_to_string('404.html')
        self.assertIn('Page Not Found', html_404)

        html_500 = render_to_string('500.html')
        self.assertIn('Internal Server Error', html_500)
