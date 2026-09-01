from rest_framework import serializers

from .models import Reminder


class ReminderSerializer(serializers.ModelSerializer):
    document_name = serializers.CharField(source="document.document_name", read_only=True)

    class Meta:
        model = Reminder
        fields = "__all__"
        read_only_fields = ("user", "sent_at", "created_at")
