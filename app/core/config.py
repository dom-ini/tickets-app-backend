from pydantic import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Survey App"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str
    SQLALCHEMY_DATABASE_URI: str
    FIRST_SUPERUSER_EMAIL: str
    FIRST_SUPERUSER_PASSWORD: str

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_ALGORITHM: str = "HS256"
    PASSWORD_REGEX: str = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@#$!%^&*()\-_=+{}[\]|\\:;<>,.?/~])(?=.*[^\s]).{8,}$"

    class Config:
        env_file = ".env"


settings = Settings()
