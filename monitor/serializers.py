from rest_framework import serializers
from .models import URL, HealthCheck


class HealthCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthCheck
        fields = ['id', 'status_code', 'response_time', 'checked_at', 'is_healthy', 'error_message']


class URLSerializer(serializers.ModelSerializer):
    latest_health_check = HealthCheckSerializer(source='get_latest_health_check', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = URL
        fields = ['id', 'name', 'url', 'created_at', 'is_active', 'latest_health_check', 'status_display']
        read_only_fields = ['created_at']


class URLCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = URL
        fields = ['name', 'url', 'is_active']
