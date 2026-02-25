"""
Celery Configuration
Background task queue for long-running operations
"""

from celery import Celery
import structlog

from app.core.config import settings

logger = structlog.get_logger()

# Create Celery app
celery_app = Celery(
    "momentaic",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

# Configure Celery
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task execution settings
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_time_limit=3600,  # 1 hour max
    task_soft_time_limit=3000,  # 50 minutes soft limit
    
    # Worker settings
    worker_prefetch_multiplier=1,
    worker_concurrency=4,
    
    # Result settings
    result_expires=86400,  # 24 hours
    
    # Task routing
    task_routes={
        "app.tasks.workflow.*": {"queue": "workflows"},
        "app.tasks.signals.*": {"queue": "signals"},
        "app.tasks.content.*": {"queue": "content"},
        "app.tasks.email.*": {"queue": "email"},
    },
    
    # Default queue
    task_default_queue="default",
    
    # Beat schedule (periodic tasks)
    beat_schedule={
        "calculate-daily-signals": {
            "task": "app.tasks.signals.calculate_all_signals",
            "schedule": 86400.0,  # Daily
        },
        "cleanup-expired-tokens": {
            "task": "app.tasks.auth.cleanup_expired_tokens",
            "schedule": 3600.0,  # Hourly
        },
        "publish-scheduled-content": {
            "task": "app.tasks.content.publish_scheduled_content",
            "schedule": 300.0,  # Every 5 minutes
        },
        "process-autopilot-leads": {
            "task": "app.tasks.growth.process_autopilot_leads",
            "schedule": 3600.0,  # Hourly
        },
        "sweep-message-bus": {
            "task": "app.tasks.message_bus_worker.sweep_message_bus",
            "schedule": 10.0,  # Every 10 seconds for real-time AI debates
        },
    },
)

# Auto-discover tasks
celery_app.autodiscover_tasks(["app.tasks"])


@celery_app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery"""
    logger.info("Celery debug task", task_id=self.request.id)
    return {"status": "ok", "task_id": self.request.id}
