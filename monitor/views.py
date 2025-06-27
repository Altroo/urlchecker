from django.shortcuts import render
from .models import URL, HealthCheck
from .serializers import URLSerializer, URLCreateSerializer, HealthCheckSerializer
from .tasks import check_url_health

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
import logging

logger = logging.getLogger(__name__)


class URLViewSet(viewsets.ModelViewSet):
    queryset = URL.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return URLCreateSerializer
        return URLSerializer

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Get health check history for a URL"""
        url_obj = self.get_object()
        health_checks = HealthCheck.objects.filter(url=url_obj)[:50]  # Last 50 checks
        serializer = HealthCheckSerializer(health_checks, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='check-now')
    def check_now(self, request, pk=None):
        """Trigger immediate health check"""
        try:
            url_obj = self.get_object()

            # Try to queue the task
            task = check_url_health.delay(url_obj.id)

            return Response({
                'message': f'Health check queued for {url_obj.name}',
                'task_id': task.id,
                'status': 'queued'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            # Any other unexpected errors and in case celery isn't running
            logger.error(f"Unexpected error in check_now: {e}")
            return Response({
                'error': 'An unexpected error occurred while queueing the health check.',
                'message': 'Internal server error',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def dashboard(request):
    """Simple dashboard view"""
    urls = URL.objects.filter(is_active=True)
    return render(request, 'dashboard.html', {'urls': urls})
