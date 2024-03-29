# pylint: disable=invalid-name,no-self-argument
import re
from typing import Callable

from pydantic import EmailStr, field_validator
from pydantic_core.core_schema import FieldValidationInfo
from pydantic_settings import BaseSettings

_PASSWORD_MIN_LENGTH = 8


class Settings(BaseSettings):
    PROJECT_NAME: str = "Tickts"
    SERVER_HOST: str
    FRONT_URL: str
    SERVER_PROTOCOL: str
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str
    ADMIN_PANEL_PATH: str
    SQLALCHEMY_DATABASE_URI: str
    SQLALCHEMY_TEST_DATABASE_URI: str

    CORS_ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]

    USERS_OPEN_REGISTRATION: bool = True
    FIRST_SUPERUSER_EMAIL: str
    FIRST_SUPERUSER_PASSWORD: str

    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 60
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_ALGORITHM: str = "HS256"
    PASSWORD_MIN_LENGTH: int = _PASSWORD_MIN_LENGTH
    PASSWORD_RULES: dict[Callable, str] = {
        lambda x: len(x) >= _PASSWORD_MIN_LENGTH: f"Password must be at least {_PASSWORD_MIN_LENGTH} characters long",
        lambda x: re.search(r"[A-Z]", x): "Password must contain at least one uppercase letter",
        lambda x: re.search(r"[a-z]", x): "Password must contain at least one lowercase letter",
        lambda x: re.search(r"\d", x): "Password must contain at least one digit",
        lambda x: re.search(
            r"[@#$!%^&*()\-_=+{}[\]|\\:;<>,.?/~\"`\']", x
        ): "Password must contain at least one special character",
    }

    SMTP_STARTTLS: bool = False
    SMTP_TLS: bool = True
    SMTP_PORT: int | None = None
    SMTP_HOST: str | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    DEFAULT_FROM_EMAIL: EmailStr | None = None
    DEFAULT_FROM_NAME: str | None = None

    @field_validator("DEFAULT_FROM_NAME")
    def get_default_from_name(cls, v: str | None, info: FieldValidationInfo) -> str:
        values = info.data
        if not v:
            return values["PROJECT_NAME"]
        return v

    EMAILS_ENABLED: bool = True
    EMAIL_TEMPLATES_DIR: str = "/app/app/email_templates/"

    @field_validator("EMAILS_ENABLED")
    def get_emails_enabled(cls, v: bool, info: FieldValidationInfo) -> bool:
        values = info.data
        is_mailing_setup = bool(
            values.get("SMTP_HOST") and values.get("SMTP_PORT") and values.get("DEFAULT_FROM_EMAIL")
        )
        if v and not is_mailing_setup:
            raise ValueError("Mailing is not set up properly")
        return v

    TEST_SUPERUSER_EMAIL: str = "superuser@example.com"
    TEST_SUPERUSER_PASSWORD: str = "Test1234!"
    TEST_USER_EMAIL: str = "user@example.com"
    TEST_USER_PASSWORD: str = "Test1234!"

    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_S3_BUCKET_NAME: str
    AWS_S3_ENDPOINT_URL: str
    AWS_DEFAULT_ACL: str
    AWS_S3_USE_SSL: bool


settings = Settings()
