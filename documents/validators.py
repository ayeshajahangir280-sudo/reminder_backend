from pathlib import Path

from django.conf import settings
from rest_framework.exceptions import ValidationError

ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}


def validate_document_file(file):
    ext = Path(file.name).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError("Only PDF, JPG, JPEG and PNG files are allowed.")
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if file.size > max_bytes:
        raise ValidationError(f"File must be {settings.MAX_UPLOAD_SIZE_MB} MB or smaller.")
    return file
