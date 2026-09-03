from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase

from documents.models import Document
from documents.services.document_scanner import DocumentScanner
from reminders.models import Reminder
from reminders.services.scheduler import calculate_reminder_date, sync_reminders
from reminders.tasks import send_due_reminders


class CoreBehaviorTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="a@example.com", email="a@example.com", password="pass12345")
        self.other = get_user_model().objects.create_user(username="b@example.com", email="b@example.com", password="pass12345")

    def make_doc(self, user=None, expiry=None):
        return Document.objects.create(user=user or self.user, document_type="Passport", document_name="Passport", expiry_date=expiry or date.today() + timedelta(days=120))

    def test_status_calculation(self):
        self.assertEqual(self.make_doc(expiry=date.today() - timedelta(days=1)).status, "Expired")
        self.assertEqual(self.make_doc(expiry=date.today() + timedelta(days=10)).status, "Urgent")
        self.assertEqual(self.make_doc(expiry=date.today() + timedelta(days=60)).status, "Expiring Soon")
        self.assertEqual(self.make_doc(expiry=date.today() + timedelta(days=120)).status, "Valid")

    def test_reminder_date_calculation(self):
        expiry = date(2027, 1, 31)
        self.assertEqual(calculate_reminder_date(expiry, "7d"), date(2027, 1, 24))

    def test_sync_reminders_prevents_duplicates(self):
        doc = self.make_doc()
        sync_reminders(doc, ["1m", "7d"], self.user.email)
        sync_reminders(doc, ["1m", "7d"], self.user.email)
        self.assertEqual(Reminder.objects.filter(document=doc).count(), 2)

    def test_due_reminder_marks_sent_once(self):
        doc = self.make_doc(expiry=date.today())
        Reminder.objects.create(user=self.user, document=doc, preset="onExpiry", reminder_date=date.today(), email=self.user.email)
        self.assertEqual(send_due_reminders(), 1)
        self.assertEqual(send_due_reminders(), 0)

    def test_scanner_does_not_invent_expiry_date(self):
        upload = SimpleUploadedFile("doc.pdf", b"%PDF-1.4\n%%EOF", content_type="application/pdf")
        result = DocumentScanner().scan(upload)
        self.assertIsNone(result["extracted_data"]["expiry_date"])

    def test_duplicate_registration_returns_validation_error(self):
        client = Client()
        payload = {
            "name": "Existing User",
            "email": self.user.email.upper(),
            "password": "pass12345X",
        }

        response = client.post("/api/auth/register/", payload, content_type="application/json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.json())
