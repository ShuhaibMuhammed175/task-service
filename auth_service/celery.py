# auth_service/celery.py
import os
from celery import Celery

# Point to your Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auth_service.settings')

# Create Celery app
app = Celery('auth_service')

# Load Celery settings from Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from installed apps
app.autodiscover_tasks()


# celery -A auth_service worker --loglevel=info
