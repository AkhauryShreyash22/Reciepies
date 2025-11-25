import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "recipies.recipies.settings")

app = Celery("recipies")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


app.conf.timezone = "Asia/Kolkata"  
app.conf.enable_utc = False

app.conf.beat_schedule = {
    "weekly-user-export": {
        "task": "reciepe_management.tasks.export_users_weekly",
        "schedule": crontab(hour=6, minute=0, day_of_week="sunday"),  
    }
}