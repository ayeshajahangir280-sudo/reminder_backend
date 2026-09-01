from django.conf import settings
from django.db import models


class Reminder(models.Model):
    PRESET_CHOICES = [("6m", "6 months before"), ("3m", "3 months before"), ("1m", "1 month before"), ("7d", "7 days before"), ("1d", "1 day before"), ("onExpiry", "On expiry date")]
    UNIT_CHOICES = [("days", "Days"), ("weeks", "Weeks"), ("months", "Months")]
    STATUS_CHOICES = [("pending", "Pending"), ("sent", "Sent"), ("cancelled", "Cancelled")]
    METHOD_CHOICES = [("email", "Email")]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reminders")
    document = models.ForeignKey("documents.Document", on_delete=models.CASCADE, related_name="reminders")
    preset = models.CharField(max_length=20, choices=PRESET_CHOICES, blank=True)
    amount = models.PositiveIntegerField(default=0)
    unit = models.CharField(max_length=12, choices=UNIT_CHOICES, default="days")
    reminder_date = models.DateField()
    notification_method = models.CharField(max_length=20, choices=METHOD_CHOICES, default="email")
    email = models.EmailField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["reminder_date"]
        constraints = [models.UniqueConstraint(fields=["document", "preset", "reminder_date", "email"], name="unique_document_reminder")]
