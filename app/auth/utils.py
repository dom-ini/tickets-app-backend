from pathlib import Path

from app.common.utils import send_email
from app.core.config import settings


def send_new_user_email(email_to: str) -> None:
    project_name = settings.PROJECT_NAME
    subject = f"[{project_name}] Welcome to {project_name}!"
    with open(Path(settings.EMAIL_TEMPLATES_DIR) / "auth/new_user.html", encoding="utf-8") as file:
        template = file.read()
    send_email(
        email_to=email_to,
        subject=subject,
        html_template=template,
        context={
            "project_name": project_name,
            "url": settings.SERVER_HOST,
        },
    )


def send_password_reset_request_mail(email_to: str, token: str) -> None:
    project_name = settings.PROJECT_NAME
    subject = f"[{project_name}] Reset your password"
    with open(Path(settings.EMAIL_TEMPLATES_DIR) / "auth/reset_password.html", encoding="utf-8") as file:
        template = file.read()
    send_email(
        email_to=email_to,
        subject=subject,
        html_template=template,
        context={
            "project_name": project_name,
            "token": token,
            "url": settings.SERVER_HOST,
        },
    )
