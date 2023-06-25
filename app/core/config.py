# pylint: disable=invalid-name,no-self-argument
from typing import Any

from pydantic import BaseSettings, EmailStr, validator


class Settings(BaseSettings):
    PROJECT_NAME: str = "Survey App"
    SERVER_HOST: str
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str
    SQLALCHEMY_DATABASE_URI: str

    USERS_OPEN_REGISTRATION: bool = True
    FIRST_SUPERUSER_EMAIL: str
    FIRST_SUPERUSER_PASSWORD: str

    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 60
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_ALGORITHM: str = "HS256"
    PASSWORD_REGEX: str = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@#$!%^&*()\-_=+{}[\]|\\:;<>,.?/~])(?=.*[^\s]).{8,}$"

    SMTP_TLS: bool = True
    SMTP_PORT: int | None = None
    SMTP_HOST: str | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    DEFAULT_FROM_EMAIL: EmailStr | None = None
    DEFAULT_FROM_NAME: str | None = None

    @validator("DEFAULT_FROM_NAME")
    def get_default_from_name(cls, v: str | None, values: dict[str, Any]) -> str:
        if not v:
            return values["PROJECT_NAME"]
        return v

    EMAILS_ENABLED: bool = True
    EMAIL_TEMPLATES_DIR: str = "/app/app/email-templates/"

    @validator("EMAILS_ENABLED", pre=True)
    def get_emails_enabled(cls, v: bool, values: dict[str, Any]) -> bool:
        is_mailing_setup = bool(
            values.get("SMTP_HOST") and values.get("SMTP_PORT") and values.get("DEFAULT_FROM_EMAIL")
        )
        if v and not is_mailing_setup:
            raise ValueError("Mailing is not set up properly")
        return v

    class Config:
        env_file = ".env"


settings = Settings()
