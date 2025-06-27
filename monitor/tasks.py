import requests
import time
import logging
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from .models import URL, HealthCheck

logger = logging.getLogger(__name__)


@shared_task(bind=True, autoretry_for=(requests.exceptions.RequestException,),
             retry_kwargs={'max_retries': 3, 'countdown': 60},
             rate_limit='30/m', retry_backoff=True)
def check_url_health(self, url_id):
    """Check if URL is responding and measure response time"""
    try:
        url_obj = URL.objects.get(id=url_id, is_active=True)
    except URL.DoesNotExist:
        logger.warning(f"URL with id {url_id} not found or inactive")
        return f"URL with id {url_id} not found or inactive"

    start_time = time.time()
    status_code = None
    error_message = None

    try:
        logger.info(f"Checking URL: {url_obj.name} ({url_obj.url})")

        headers = {
            'User-Agent': 'URLChecker/1.0 (Health Monitor)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }

        response = requests.get(
            url_obj.url,
            timeout=30,
            headers=headers,
            allow_redirects=True,
            verify=True
        )
        status_code = response.status_code
        response_time = time.time() - start_time
        is_healthy = 200 <= status_code < 400

        logger.info(f"URL {url_obj.name}: Status {status_code}, Time {response_time:.3f}s")

    except requests.exceptions.Timeout:
        response_time = time.time() - start_time
        error_message = "Request timeout"
        is_healthy = False
        logger.warning(f"Timeout checking {url_obj.name}: {error_message}")

    except requests.exceptions.SSLError as e:
        response_time = time.time() - start_time
        error_message = f"SSL error: {str(e)[:100]}"
        is_healthy = False
        logger.warning(f"SSL error checking {url_obj.name}: {error_message}")

    except requests.exceptions.ConnectionError:
        response_time = time.time() - start_time
        error_message = "Connection failed"
        is_healthy = False
        logger.warning(f"Connection error checking {url_obj.name}: {error_message}")

    except requests.exceptions.RequestException as e:
        response_time = time.time() - start_time
        error_message = f"Request error: {str(e)[:100]}"
        is_healthy = False
        logger.error(f"Request error checking {url_obj.name}: {error_message}")

        # If all retries failed, save the error and return
        if self.request.retries >= self.max_retries:
            with transaction.atomic():
                health_check = HealthCheck.objects.create(
                    url=url_obj,
                    status_code=None,
                    response_time=response_time,
                    is_healthy=is_healthy,
                    error_message=error_message
                )
                logger.debug(f"Saved health check {health_check.id} for {url_obj.name}")
            return f"Checked {url_obj.name}: Unhealthy ({error_message})"

        # If not all retries failed, retry the task
        else:
            logger.info(f"Retrying {url_obj.name} (attempt {self.request.retries + 1})")
            raise self.retry(countdown=60 * (self.request.retries + 1))

    # Save to a database with transaction safety
    # Either the operation completes successfully, or it's completely rolled back
    try:
        with transaction.atomic():
            health_check = HealthCheck.objects.create(
                url=url_obj,
                status_code=status_code,
                response_time=response_time,
                is_healthy=is_healthy,
                error_message=error_message
            )
            logger.debug(f"Saved health check {health_check.id} for {url_obj.name}")

    except Exception as e:
        logger.error(f"Database error saving health check for {url_obj.name}: {e}")

    result = f"Checked {url_obj.name}: {'Healthy' if is_healthy else 'Unhealthy'}"
    if error_message:
        result += f" ({error_message})"

    return result


@shared_task(bind=True)
def check_all_urls(self):
    """Periodic task to check all active URLs - runs every 5 minutes via Celery Beat"""
    try:
        active_urls = URL.objects.filter(is_active=True)
        queued_count = 0

        logger.info(f"Starting scheduled batch health check for {active_urls.count()} URLs")

        for url_obj in active_urls:
            try:
                check_url_health.apply_async(
                    args=[url_obj.id],
                    countdown=queued_count * 2
                )
                queued_count += 1

            except Exception as e:
                logger.error(f"Error queueing check for {url_obj.name}: {e}")

        logger.info(f"Scheduled check: Queued {queued_count} URL health checks")
        return f"Queued {queued_count} URL checks"

    except Exception as e:
        logger.error(f"Error in scheduled check_all_urls: {e}")
        raise


@shared_task(bind=True)
def cleanup_old_records(self):
    """Delete health checks older than 3 days - runs daily at midnight via Celery Beat"""
    try:
        cutoff_date = timezone.now() - timedelta(days=3)

        logger.info(f"Starting scheduled cleanup of health checks older than {cutoff_date}")

        deleted_count, deleted_types = HealthCheck.objects.filter(
            checked_at__lt=cutoff_date
        ).delete()

        logger.info(f"Scheduled cleanup completed: deleted {deleted_count} old health check records")
        return f"Deleted {deleted_count} old health check records"

    except Exception as e:
        logger.error(f"Error in scheduled cleanup_old_records: {e}")
        raise


@shared_task(bind=True, rate_limit='5/m')
def bulk_check_urls(self, url_ids):
    """Check multiple URLs efficiently - for manual/API triggers"""
    if not url_ids:
        return "No URLs to check"

    try:
        logger.info(f"Starting manual bulk check for {len(url_ids)} URLs")

        for i, url_id in enumerate(url_ids):
            check_url_health.apply_async(
                args=[url_id],
                countdown=i * 1
            )

        return f"Queued {len(url_ids)} URL checks"

    except Exception as e:
        logger.error(f"Error in bulk_check_urls: {e}")
        raise
