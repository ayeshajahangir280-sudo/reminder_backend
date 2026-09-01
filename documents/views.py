from datetime import date, timedelta

from django.db import transaction
from django.db.models import Count, Q
from rest_framework import decorators, parsers, response, status, viewsets

from notifications.models import Notification
from reminders.services.scheduler import sync_reminders
from .models import Document
from .serializers import ConfirmScannedDocumentSerializer, DocumentSerializer, RenewDocumentSerializer
from .services.document_scanner import DocumentScanner
from .validators import validate_document_file


class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    search_fields = ("document_name", "holder_name", "document_number", "document_type")
    filterset_fields = ("document_type", "archived")
    ordering_fields = ("expiry_date", "created_at", "updated_at")
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def get_queryset(self):
        qs = Document.objects.filter(user=self.request.user)
        status_filter = self.request.query_params.get("status")
        today = date.today()
        if status_filter == "Expired":
            qs = qs.filter(expiry_date__lt=today)
        elif status_filter == "Urgent":
            qs = qs.filter(expiry_date__gte=today, expiry_date__lte=today + timedelta(days=30))
        elif status_filter == "Expiring Soon":
            qs = qs.filter(expiry_date__gt=today + timedelta(days=30), expiry_date__lte=today + timedelta(days=90))
        elif status_filter == "Valid":
            qs = qs.filter(expiry_date__gt=today + timedelta(days=90))
        return qs

    def perform_create(self, serializer):
        doc = serializer.save(user=self.request.user, user_verified=True)
        Notification.objects.create(user=self.request.user, document=doc, event="document_added", title=f"{doc.document_name} added", body=f"Expires on {doc.expiry_date}.")

    @decorators.action(detail=False, methods=["get"])
    def dashboard(self, request):
        docs = self.get_queryset().filter(archived=False)
        today = date.today()
        data = {
            "total_documents": docs.count(),
            "expired": docs.filter(expiry_date__lt=today).count(),
            "urgent": docs.filter(expiry_date__gte=today, expiry_date__lte=today + timedelta(days=30)).count(),
            "expiring_soon": docs.filter(expiry_date__gte=today, expiry_date__lte=today + timedelta(days=90)).count(),
            "upcoming_reminders": request.user.reminders.filter(status="pending", reminder_date__gte=today).order_by("reminder_date")[:10].values(),
            "upcoming_expiries": DocumentSerializer(docs.filter(expiry_date__gte=today).order_by("expiry_date")[:10], many=True).data,
        }
        return response.Response(data)

    @decorators.action(detail=False, methods=["post"], parser_classes=[parsers.MultiPartParser])
    def scan(self, request):
        file = request.FILES.get("file")
        if not file:
            return response.Response({"detail": "file is required."}, status=400)
        validate_document_file(file)
        result = DocumentScanner().scan(file, request.data.get("document_type"))
        return response.Response(result)

    @decorators.action(detail=False, methods=["post"])
    @transaction.atomic
    def confirm(self, request):
        serializer = ConfirmScannedDocumentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reminders = serializer.validated_data.pop("reminders", [])
        doc = Document.objects.create(user=request.user, user_verified=True, extracted_data=request.data, ai_confidence=request.data.get("ai_confidence", 0), **serializer.validated_data)
        sync_reminders(doc, reminders, request.user.email)
        Notification.objects.create(user=request.user, document=doc, event="document_added", title=f"{doc.document_name} added", body=f"{len(reminders)} reminders scheduled.")
        return response.Response(DocumentSerializer(doc).data, status=status.HTTP_201_CREATED)

    @decorators.action(detail=True, methods=["post"])
    def archive(self, request, pk=None):
        doc = self.get_object()
        doc.archived = True
        doc.save(update_fields=["archived", "updated_at"])
        return response.Response(DocumentSerializer(doc).data)

    @decorators.action(detail=True, methods=["post"], url_path="reminders")
    def set_reminders(self, request, pk=None):
        doc = self.get_object()
        presets = request.data.get("reminders", [])
        reminders = sync_reminders(doc, presets, request.user.email)
        return response.Response({"reminders": [r.preset for r in reminders]})

    @decorators.action(detail=True, methods=["post"], parser_classes=[parsers.MultiPartParser, parsers.FormParser])
    @transaction.atomic
    def renew(self, request, pk=None):
        old = self.get_object()
        serializer = RenewDocumentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reminders = serializer.validated_data.pop("reminders", [])
        old.archived = True
        old.save(update_fields=["archived", "updated_at"])
        new = Document.objects.create(user=request.user, previous_version=old, user_verified=True, extracted_data=request.data, ai_confidence=request.data.get("ai_confidence", 0), **serializer.validated_data)
        sync_reminders(new, reminders, request.user.email)
        Notification.objects.create(user=request.user, document=new, event="document_renewed", title=f"{new.document_name} renewed", body=f"New expiry date: {new.expiry_date}.")
        return response.Response(DocumentSerializer(new).data, status=status.HTTP_201_CREATED)
