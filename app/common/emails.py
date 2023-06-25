from typing import Any

import emails
from emails.template import JinjaTemplate

from app.core.config import settings
from app.logging import logger


def send_email(
    email_to: str,
    subject: str = "",
    html_template: str = "",
    context: dict[str, Any] | None = None,
) -> None:
    assert settings.EMAILS_ENABLED, "no provided configuration for email variables"
    if context is None:
        context = {}
    message = emails.Message(
        subject=JinjaTemplate(subject),
        html=JinjaTemplate(html_template),
        mail_from=(settings.DEFAULT_FROM_NAME, settings.DEFAULT_FROM_EMAIL),
    )
    smtp_options = {"host": settings.SMTP_HOST, "port": settings.SMTP_PORT, "tls": settings.SMTP_TLS}
    if settings.SMTP_USER and settings.SMTP_PASSWORD:
        smtp_options.update({"user": settings.SMTP_USER, "password": settings.SMTP_PASSWORD})
    response = message.send(to=email_to, render=context, smtp=smtp_options)
    logger.info(f"send email result: {response}")
