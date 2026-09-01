# Doc Sentinel Backend

Django REST backend for the React Document Expiry Reminder app.

## Setup

1. Create and activate a virtual environment.
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and update PostgreSQL, Redis, email, and secret values.
4. Create the PostgreSQL database named in `DATABASE_URL`.
5. Run migrations: `python manage.py migrate`
6. Start the API: `python manage.py runserver`
7. Start workers:
   - `celery -A config worker -l info`
   - `celery -A config beat -l info`

## API

Auth endpoints are under `/api/auth/`. Main resources are `/api/documents/`, `/api/reminders/`, and `/api/notifications/`.

Important document actions:

- `POST /api/documents/scan/`
- `POST /api/documents/confirm/`
- `POST /api/documents/{id}/archive/`
- `POST /api/documents/{id}/renew/`
- `GET /api/documents/dashboard/`
