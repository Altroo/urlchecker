from django.contrib import admin
from .models import URL, HealthCheck


@admin.register(URL)
class URLAdmin(admin.ModelAdmin):
    list_display = ['name', 'url', 'is_active', 'created_at', 'get_status_display']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'url']


@admin.register(HealthCheck)
class HealthCheckAdmin(admin.ModelAdmin):
    list_display = ['url', 'status_code', 'response_time', 'is_healthy', 'checked_at']
    list_filter = ['is_healthy', 'status_code', 'checked_at']
    search_fields = ['url__name', 'url__url']
