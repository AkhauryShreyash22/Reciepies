from django.apps import AppConfig


class ReciepeManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reciepe_management'

class ReciepeManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reciepe_management'

    def ready(self):
        from django_celery_beat.models import CrontabSchedule, PeriodicTask
        from django.db.utils import OperationalError, ProgrammingError

        try:
            schedule, created = CrontabSchedule.objects.get_or_create(
                minute="0",
                hour="6",
                day_of_week="mon-fri",   
                day_of_month="*",
                month_of_year="*",
                timezone="Asia/Kolkata",
            )

            PeriodicTask.objects.get_or_create(
                name="send_daily_emails_monday_to_friday_6am",
                task="reciepe_management.tasks.send_daily_emails",
                crontab=schedule,
                defaults={"enabled": True}
            )

        except (OperationalError, ProgrammingError):
            pass