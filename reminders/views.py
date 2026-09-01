from rest_framework import viewsets

from .models import Reminder
from .serializers import ReminderSerializer


class ReminderViewSet(viewsets.ModelViewSet):
    serializer_class = ReminderSerializer
    filterset_fields = ("document", "status", "notification_method")
    ordering_fields = ("reminder_date", "created_at")

    def get_queryset(self):
        return Reminder.objects.filter(user=self.request.user).select_related("document")

    def perform_create(self, serializer):
        document = serializer.validated_data["document"]
        if document.user_id != self.request.user.id:
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied("Cannot create reminders for another user's document.")
        serializer.save(user=self.request.user)
