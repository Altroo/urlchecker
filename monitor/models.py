from django.db import models


class URL(models.Model):
    name = models.CharField(max_length=255)
    url = models.URLField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.url}"

    def get_latest_health_check(self):
        return self.healthcheck_set.first()

    def get_status_display(self):
        latest = self.get_latest_health_check()
        if not latest:
            return "Never checked"
        return "Healthy" if latest.is_healthy else "Unhealthy"


class HealthCheck(models.Model):
    url = models.ForeignKey(URL, on_delete=models.CASCADE)
    status_code = models.IntegerField(null=True, blank=True)
    response_time = models.FloatField(null=True, blank=True)  # in seconds
    checked_at = models.DateTimeField(auto_now_add=True)
    is_healthy = models.BooleanField(default=False)
    error_message = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-checked_at']

    def __str__(self):
        return f"{self.url.name} - {self.status_code} - {self.checked_at}"
