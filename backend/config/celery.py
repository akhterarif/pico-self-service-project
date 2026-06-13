import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("pico")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


app.conf.beat_schedule = {
    "send-unpaid-invoice-notification": {
        "task": "billing.tasks.send_unpaid_invoice_notification",
        "schedule": crontab(hour=0, minute=0),
    },
    "make-invoice-overdue": {
        "task": "billing.tasks.make_invoice_overdue",
        "schedule": crontab(hour=0, minute=0),
    },
    "stop-overdue-vms": {
        "task": "billing.tasks.stop_overdue_vms",
        "schedule": crontab(hour=1, minute=0),
    },
}
