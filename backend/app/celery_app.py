"""
Configuration Celery pour les tâches en arrière-plan
"""
from celery import Celery
from app.config import settings
import os

# Configuration Redis pour Celery
redis_url = settings.redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "kairos",
    broker=redis_url,
    backend=redis_url,
    include=[
        "app.tasks.exam_generation",
        "app.tasks.pdf_generation",
        "app.tasks.analytics"
    ]
)

# Configuration Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max par tâche
    task_soft_time_limit=240,  # 4 minutes soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
)
