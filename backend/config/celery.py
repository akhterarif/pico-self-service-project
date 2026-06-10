import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("pico")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# Schedule to update vector DB every hour
app.conf.beat_schedule = {
	"index-vectors-every-hour": {
		"task": "apps.ai.tasks.index_vectors_task",
		"schedule": crontab(minute=0, hour="*"),
	}
}
