# HCLV CareerNet

Flask-based careers/student portal application.

## Stack
- Python 3.12, Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF
- SQLite database (`instance/hclv.db`)
- Gunicorn for production

## Running
- Dev: `python app.py` — serves on `0.0.0.0:5000` (configured in workflow "Start application")
- Prod: `gunicorn --bind=0.0.0.0:5000 --reuse-port "app:create_app()"`

## Notes
- Default SuperUser is only seeded if `DEFAULT_SU_PASSWORD` env var is set (optional `DEFAULT_SU_USERNAME`, default `su2026`).
- `SECRET_KEY` should be set in production.

## Password Reset (Forgot Password)
- Flow: `/forgot-password` → `/verify-reset-code` → `/reset-password`
- Sends a 6-digit numeric code (15-min TTL, max 5 attempts) to the email stored on the student profile.
- Email is delivered via Outlook SMTP (`smtp-mail.outlook.com:587`, STARTTLS).
- Required secrets: `OUTLOOK_EMAIL`, `OUTLOOK_PASSWORD` (use an App Password if 2FA is enabled).
- Implementation: `email_service.py`, routes in `routes/auth.py`, model `PasswordResetCode` in `models.py`.
