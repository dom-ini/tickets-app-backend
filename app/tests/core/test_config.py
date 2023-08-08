import pytest
from pydantic import ValidationError

from app.core.config import Settings


class TestConfig:
    def test_default_from_name(self) -> None:
        default_from = "DEFAULT_FROM"
        project_name = "PROJECT_NAME"
        config = Settings(DEFAULT_FROM_NAME=default_from, PROJECT_NAME=project_name)
        assert config.DEFAULT_FROM_NAME == default_from

    def test_default_from_name_should_default_to_project_name(self) -> None:
        project_name = "PROJECT_NAME"
        config = Settings(PROJECT_NAME=project_name)
        assert config.DEFAULT_FROM_NAME == project_name

    def test_emails_enabled_with_no_configuration_should_fail(self) -> None:
        emails_enabled = True
        smtp_host = ""
        with pytest.raises(ValidationError):
            Settings(EMAILS_ENABLED=emails_enabled, SMTP_HOST=smtp_host)
