from django.conf import settings
from celery import Celery
from os import environ

# Set the default Django settings module for the 'celery' program.
environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.local")

# Create the Celery app
app = Celery("nebeshtgah")

# Load configuration from Django settings
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks in all installed apps
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# Optional: Set up periodic tasks (beat schedule)
app.conf.beat_schedule = {
    "run-every-30-seconds": {
        "task": "myapp.tasks.my_periodic_task",
        "schedule": 30.0,  # Run every 30 seconds
        "args": (16, 16),  # Optional arguments
    },
}

# Optional: Configure result backend
app.conf.result_backend = "django-db"  # Use Django database as the result backend

# Optional: Configure task timeouts and retries
app.conf.task_time_limit = 300  # 5 minutes
app.conf.task_soft_time_limit = 240  # 4 minutes
app.conf.task_acks_late = True  # Acknowledge tasks after they are executed
app.conf.task_reject_on_worker_lost = True  # Re-enqueue tasks if the worker is lost
