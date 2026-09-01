from django.core.mail import send_mail


def send_reminder_email(reminder):
    doc = reminder.document
    subject = f"Renewal reminder: {doc.document_name}"
    body = (
        f"{doc.document_name} ({doc.document_type}) expires on {doc.expiry_date}.\n"
        f"Days remaining: {doc.days_remaining}.\n\n"
        "Please renew it before expiry to avoid disruption."
    )
    send_mail(subject, body, None, [reminder.email], fail_silently=False)
