from django.db import transaction
from django.utils import timezone

from config.celery import app
from notifications.models import Notification
from .models import Reminder
from .services.emailer import send_reminder_email


@app.task
def send_due_reminders():
    today = timezone.localdate()
    sent = 0
    with transaction.atomic():
        due = Reminder.objects.select_for_update().filter(status="pending", reminder_date__lte=today)
        for reminder in due:
            send_reminder_email(reminder)
            reminder.status = "sent"
            reminder.sent_at = timezone.now()
            reminder.save(update_fields=["status", "sent_at"])
            Notification.objects.create(user=reminder.user, document=reminder.document, event="reminder_sent", title=f"Reminder sent for {reminder.document.document_name}", body=f"Expiry date: {reminder.document.expiry_date}.")
            sent += 1
    return sent
