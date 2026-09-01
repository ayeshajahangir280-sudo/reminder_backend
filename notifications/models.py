from django.conf import settings
from django.db import models


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    document = models.ForeignKey("documents.Document", null=True, blank=True, on_delete=models.CASCADE, related_name="notifications")
    event = models.CharField(max_length=60)
    title = models.CharField(max_length=160)
    body = models.TextField(blank=True)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
