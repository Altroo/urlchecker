import requests
from django.test import TestCase
from unittest.mock import patch, Mock
from monitor.models import URL, HealthCheck
from monitor.tasks import check_url_health


class TaskTest(TestCase):
    @patch('monitor.tasks.requests.get')
    def test_check_url_health_task_success(self, mock_get):
        # Mock successful HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        url = URL.objects.create(
            name="Test Site",
            url="https://example.com"
        )
        result = check_url_health(url.id)
        self.assertIn("Checked", result)
        self.assertIn("Healthy", result)

        # Check that a health check record was created
        health_check = HealthCheck.objects.filter(url=url).first()
        self.assertIsNotNone(health_check)
        self.assertEqual(health_check.status_code, 200)
        self.assertTrue(health_check.is_healthy)

    def test_check_url_health_task_nonexistent_url(self):
        result = check_url_health(99999)  # Non-existent URL ID
        self.assertIn("not found", result)

    def test_check_url_health_task_inactive_url(self):
        url = URL.objects.create(
            name="Test Site",
            url="https://example.com",
            is_active=False
        )
        result = check_url_health(url.id)
        self.assertIn("not found or inactive", result)

    @patch('monitor.tasks.requests.get')
    def test_check_url_health_task_request_exception(self, mock_get):
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection error")

        url = URL.objects.create(
            name="Test Site",
            url="https://example.com"
        )
        result = check_url_health(url.id)
        self.assertIn("Checked", result)
        self.assertIn("Unhealthy", result)

        # Check that a health check record was created with an error
        health_check = HealthCheck.objects.filter(url=url).first()
        self.assertIsNotNone(health_check)
        self.assertIsNone(health_check.status_code)
        self.assertFalse(health_check.is_healthy)
        self.assertIsNotNone(health_check.error_message)
