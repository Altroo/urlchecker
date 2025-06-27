from django.test import TestCase
from rest_framework.test import APITestCase
from unittest.mock import patch, Mock
from monitor.models import URL, HealthCheck


class URLAPITest(APITestCase):
    def test_create_url(self):
        data = {
            'name': 'Test Site',
            'url': 'https://example.com'
        }
        response = self.client.post('/api/urls/', data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['name'], 'Test Site')
        self.assertEqual(response.data['url'], 'https://example.com')

    def test_list_urls(self):
        URL.objects.create(name="Test Site", url="https://example.com")
        response = self.client.get('/api/urls/')
        self.assertEqual(response.status_code, 200)
        # Check if pagination is used or direct results
        data = response.data
        if 'results' in data:
            self.assertEqual(len(data['results']), 1)
        else:
            self.assertEqual(len(data), 1)

    def test_get_url_detail(self):
        url = URL.objects.create(name="Test Site", url="https://example.com")
        response = self.client.get(f'/api/urls/{url.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'Test Site')

    def test_delete_url(self):
        url = URL.objects.create(name="Test Site", url="https://example.com")
        response = self.client.delete(f'/api/urls/{url.id}/')
        self.assertEqual(response.status_code, 204)
        self.assertFalse(URL.objects.filter(id=url.id).exists())

    @patch('monitor.tasks.check_url_health.delay')
    def test_check_now_endpoint(self, mock_delay):
        # Mock the delay method to return a task with an id
        mock_task = Mock()
        mock_task.id = 'test-task-id'
        mock_delay.return_value = mock_task

        url = URL.objects.create(name="Test Site", url="https://example.com")
        response = self.client.post(f'/api/urls/{url.id}/check-now/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('task_id', response.data)
        self.assertEqual(response.data['task_id'], 'test-task-id')
        mock_delay.assert_called_once_with(url.id)

    def test_history_endpoint(self):
        url = URL.objects.create(name="Test Site", url="https://example.com")
        HealthCheck.objects.create(
            url=url,
            status_code=200,
            response_time=0.5,
            is_healthy=True
        )
        response = self.client.get(f'/api/urls/{url.id}/history/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)


class DashboardViewTest(TestCase):
    def test_dashboard_view(self):
        URL.objects.create(name="Test Site", url="https://example.com")
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "URL Health Monitor")
        self.assertContains(response, "Test Site")

    def test_dashboard_view_only_active_urls(self):
        URL.objects.create(name="Active Site", url="https://example.com", is_active=True)
        URL.objects.create(name="Inactive Site", url="https://test.com", is_active=False)
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Active Site")
        self.assertNotContains(response, "Inactive Site")
