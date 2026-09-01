from rest_framework import serializers

from reminders.models import Reminder
from .models import Document
from .validators import validate_document_file


class DocumentSerializer(serializers.ModelSerializer):
    status = serializers.CharField(read_only=True)
    days_remaining = serializers.IntegerField(read_only=True)

    class Meta:
        model = Document
        fields = "__all__"
        read_only_fields = ("user", "extracted_data", "ai_confidence", "user_verified", "created_at", "updated_at")

    def validate_document_file(self, value):
        return validate_document_file(value)


class ConfirmScannedDocumentSerializer(serializers.Serializer):
    scan_id = serializers.CharField(required=False, allow_blank=True)
    document_type = serializers.ChoiceField(choices=Document.TYPE_CHOICES)
    document_name = serializers.CharField(max_length=160)
    holder_name = serializers.CharField(max_length=160, allow_blank=True, required=False)
    document_number = serializers.CharField(max_length=120, allow_blank=True, required=False)
    issue_date = serializers.DateField(required=False, allow_null=True)
    expiry_date = serializers.DateField()
    date_of_birth = serializers.DateField(required=False, allow_null=True)
    nationality = serializers.CharField(max_length=100, allow_blank=True, required=False)
    issuing_country = serializers.CharField(max_length=100, allow_blank=True, required=False)
    issuing_authority = serializers.CharField(max_length=160, allow_blank=True, required=False)
    reminders = serializers.ListField(child=serializers.ChoiceField(choices=Reminder.PRESET_CHOICES), required=False)


class RenewDocumentSerializer(ConfirmScannedDocumentSerializer):
    document_file = serializers.FileField(required=False)

    def validate_document_file(self, value):
        return validate_document_file(value)
