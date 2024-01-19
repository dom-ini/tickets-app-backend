from fastapi_mail import MessageSchema

from app.common.emails import prepare_email


def send_new_user_email(email_to: str, verification_token: str) -> MessageSchema:
    subject = "Witamy w {{ project_name }}!"
    return prepare_email(
        email_to=[email_to],
        subject=subject,
        template_name="auth/new_user.html",
        context={
            "token": verification_token,
        },
    )


def send_password_reset_request_mail(email_to: str, token: str) -> MessageSchema:
    subject = "Zresetuj swoje hasło"
    return prepare_email(
        email_to=[email_to],
        subject=subject,
        template_name="auth/reset_password.html",
        context={
            "token": token,
        },
    )
