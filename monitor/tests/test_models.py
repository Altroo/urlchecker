from django.test import TestCase
from monitor.models import URL, HealthCheck


class URLModelTest(TestCase):
    def test_url_creation(self):
        url = URL.objects.create(
            name="Test Site",
            url="https://example.com"
        )
        self.assertEqual(url.name, "Test Site")
        self.assertEqual(url.url, "https://example.com")
        self.assertTrue(url.is_active)

    def test_url_string_representation(self):
        url = URL.objects.create(
            name="Test Site",
            url="https://example.com"
        )
        self.assertEqual(str(url), "Test Site - https://example.com")

    def test_get_status_display(self):
        url = URL.objects.create(
            name="Test Site",
            url="https://example.com"
        )
        self.assertEqual(url.get_status_display(), "Never checked")

    def test_get_status_display_with_health_check(self):
        url = URL.objects.create(
            name="Test Site",
            url="https://example.com"
        )
        HealthCheck.objects.create(
            url=url,
            status_code=200,
            response_time=0.5,
            is_healthy=True
        )
        self.assertEqual(url.get_status_display(), "Healthy")


class HealthCheckModelTest(TestCase):
    def test_health_check_creation(self):
        url = URL.objects.create(
            name="Test Site",
            url="https://example.com"
        )
        health_check = HealthCheck.objects.create(
            url=url,
            status_code=200,
            response_time=0.5,
            is_healthy=True
        )
        self.assertEqual(health_check.status_code, 200)
        self.assertEqual(health_check.response_time, 0.5)
        self.assertTrue(health_check.is_healthy)

    def test_health_check_string_representation(self):
        url = URL.objects.create(
            name="Test Site",
            url="https://example.com"
        )
        health_check = HealthCheck.objects.create(
            url=url,
            status_code=200,
            response_time=0.5,
            is_healthy=True
        )
        expected_str = f"Test Site - 200 - {health_check.checked_at}"
        self.assertEqual(str(health_check), expected_str)
