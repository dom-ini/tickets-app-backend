from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator, Iterable, Protocol

from emails.template import JinjaTemplate
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema

from app.core.config import settings


class MailEngine(Protocol):  # pragma: no cover
    async def send_message(self, message: Any, template_name: str = ...) -> None:
        ...

    @contextmanager
    def record_messages(self) -> Generator:
        ...


class MailSender:
    def __init__(self, engine: MailEngine) -> None:
        self.engine = engine

    async def send(self, message: Any) -> None:
        return await self.engine.send_message(message)

    @contextmanager
    def record_messages(self) -> Generator:
        with self.engine.record_messages() as outbox:
            yield outbox


def read_template(template_name: str) -> str:
    with open(Path(settings.EMAIL_TEMPLATES_DIR) / template_name, encoding="utf-8") as file:
        return file.read()


def prepare_email(
    email_to: Iterable[str],
    subject: str,
    template_name: str,
    context: dict[str, Any] | None = None,
) -> MessageSchema:
    base_context = {
        "project_name": settings.PROJECT_NAME,
        "url": settings.SERVER_HOST,
    }
    if context is not None:
        base_context.update(context)
    subject = JinjaTemplate(subject).render(**base_context)
    template = read_template(template_name)
    body = JinjaTemplate(template).render(**base_context)
    message = MessageSchema(
        recipients=email_to,
        subject=subject,
        body=body,
        subtype="html",
    )
    return message


def get_mailer_config() -> dict[str, Any]:
    return {
        "MAIL_USERNAME": settings.SMTP_USER,
        "MAIL_PASSWORD": settings.SMTP_PASSWORD,
        "MAIL_PORT": settings.SMTP_PORT,
        "MAIL_SERVER": settings.SMTP_HOST,
        "MAIL_FROM": settings.DEFAULT_FROM_EMAIL,
        "MAIL_FROM_NAME": settings.DEFAULT_FROM_NAME,
        "MAIL_STARTTLS": settings.SMTP_STARTTLS,
        "MAIL_SSL_TLS": settings.SMTP_TLS,
    }


def mailer() -> MailSender:
    config = ConnectionConfig(**get_mailer_config())
    engine = FastMail(config)
    return MailSender(engine)
