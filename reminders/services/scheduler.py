from datetime import timedelta

from reminders.models import Reminder

PRESET_DAYS = {"6m": 180, "3m": 90, "1m": 30, "7d": 7, "1d": 1, "onExpiry": 0}


def calculate_reminder_date(expiry_date, preset):
    return expiry_date - timedelta(days=PRESET_DAYS[preset])


def sync_reminders(document, presets, email):
    document.reminders.filter(status="pending").delete()
    created = []
    for preset in presets:
        reminder_date = calculate_reminder_date(document.expiry_date, preset)
        reminder, _ = Reminder.objects.get_or_create(
            user=document.user,
            document=document,
            preset=preset,
            reminder_date=reminder_date,
            email=email,
            defaults={"amount": PRESET_DAYS[preset], "unit": "days"},
        )
        created.append(reminder)
    return created
