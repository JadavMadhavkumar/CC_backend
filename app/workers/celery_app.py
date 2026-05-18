"""
Celery application for background tasks.
"""

from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "carbon_credit_platform",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.workers.tasks"
    ]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
    task_soft_time_limit=3000,
)


@celery_app.task(name="app.workers.health_check")
def health_check() -> dict:
    """Health check task."""
    return {"status": "healthy"}


if __name__ == "__main__":
    celery_app.start()