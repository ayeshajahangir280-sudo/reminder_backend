import re
from datetime import datetime
from pathlib import Path

from pypdf import PdfReader

DATE_PATTERNS = [
    "%Y-%m-%d",
    "%d/%m/%Y",
    "%d-%m-%Y",
    "%d.%m.%Y",
    "%d %b %Y",
    "%d %B %Y",
]


class DocumentScanner:
    def scan(self, file, selected_type=None):
        text = self._extract_text(file)
        extracted = self._parse_text(text)
        if selected_type and selected_type != "auto":
            extracted["document_type"] = selected_type
        confidence = self._confidence(extracted, text)
        return {
            "extracted_data": extracted,
            "confidence": confidence,
            "raw_text": text[:5000],
            "warnings": [] if extracted.get("expiry_date") else ["Expiry date could not be confidently detected."],
        }

    def _extract_text(self, file):
        suffix = Path(file.name).suffix.lower()
        file.seek(0)
        if suffix == ".pdf":
            try:
                reader = PdfReader(file)
                return "\n".join(page.extract_text() or "" for page in reader.pages)
            except Exception:
                return ""
        try:
            import pytesseract
            from PIL import Image

            return pytesseract.image_to_string(Image.open(file))
        except Exception:
            return ""

    def _parse_text(self, text):
        return {
            "document_type": self._detect_type(text),
            "holder_name": self._label(text, ["name", "holder name", "full name"]),
            "document_number": self._label(text, ["document no", "document number", "passport no", "licence no", "id number"]),
            "issue_date": self._near_date(text, ["issue", "issued"]),
            "expiry_date": self._near_date(text, ["expiry", "expires", "valid until", "date of expiry"]),
            "date_of_birth": self._near_date(text, ["birth", "dob", "date of birth"]),
            "nationality": self._label(text, ["nationality"]),
            "issuing_country": self._label(text, ["issuing country", "country"]),
            "issuing_authority": self._label(text, ["authority", "issuing authority"]),
        }

    def _detect_type(self, text):
        lowered = text.lower()
        for value in ["passport", "visa", "emirates id", "driving licence", "insurance", "trade licence", "vehicle registration", "contract"]:
            if value in lowered:
                return value.title() if value != "emirates id" else "Emirates ID"
        return "Other"

    def _label(self, text, labels):
        for label in labels:
            match = re.search(rf"{re.escape(label)}\s*[:#-]?\s*([A-Z0-9][A-Z0-9 /\-.]{{2,80}})", text, re.I)
            if match:
                return match.group(1).strip()
        return ""

    def _near_date(self, text, labels):
        for label in labels:
            match = re.search(rf"{re.escape(label)}[^\n\r]{{0,40}}?(\d{{4}}-\d{{2}}-\d{{2}}|\d{{1,2}}[./-]\d{{1,2}}[./-]\d{{2,4}}|\d{{1,2}}\s+[A-Za-z]{{3,9}}\s+\d{{4}})", text, re.I)
            if match:
                parsed = self._parse_date(match.group(1))
                if parsed:
                    return parsed
        return None

    def _parse_date(self, value):
        for fmt in DATE_PATTERNS:
            try:
                return datetime.strptime(value, fmt).date().isoformat()
            except ValueError:
                continue
        return None

    def _confidence(self, extracted, text):
        if not text.strip():
            return 0
        score = 30
        score += 25 if extracted.get("expiry_date") else 0
        score += 10 if extracted.get("document_number") else 0
        score += 10 if extracted.get("holder_name") else 0
        score += 10 if extracted.get("document_type") != "Other" else 0
        return min(score, 95)
