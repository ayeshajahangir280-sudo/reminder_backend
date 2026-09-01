import uuid
from datetime import date

from django.conf import settings
from django.db import models


def document_upload_path(instance, filename):
    ext = filename.rsplit(".", 1)[-1].lower()
    return f"documents/{instance.user_id}/{uuid.uuid4()}.{ext}"


class Document(models.Model):
    TYPE_CHOICES = [(v, v) for v in ["Passport", "Visa", "Emirates ID", "Driving Licence", "Insurance", "Trade Licence", "Vehicle Registration", "Contract", "Other"]]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="documents")
    previous_version = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="renewals")
    document_type = models.CharField(max_length=64, choices=TYPE_CHOICES)
    document_name = models.CharField(max_length=160)
    holder_name = models.CharField(max_length=160, blank=True)
    document_number = models.CharField(max_length=120, blank=True)
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField()
    date_of_birth = models.DateField(null=True, blank=True)
    nationality = models.CharField(max_length=100, blank=True)
    issuing_country = models.CharField(max_length=100, blank=True)
    issuing_authority = models.CharField(max_length=160, blank=True)
    document_file = models.FileField(upload_to=document_upload_path, null=True, blank=True)
    extracted_data = models.JSONField(default=dict, blank=True)
    ai_confidence = models.PositiveSmallIntegerField(default=0)
    user_verified = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["expiry_date", "-created_at"]

    @property
    def days_remaining(self):
        return (self.expiry_date - date.today()).days

    @property
    def status(self):
        days = self.days_remaining
        if days < 0:
            return "Expired"
        if days <= 30:
            return "Urgent"
        if days <= 90:
            return "Expiring Soon"
        return "Valid"
