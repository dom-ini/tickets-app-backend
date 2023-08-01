import pytest
from pydantic import ValidationError

from app.core.config import Settings


class TestConfig:
    def test_default_from_name(self) -> None:
        default_from = "DEFAULT_FROM"
        project_name = "PROJECT_NAME"
        config_data = {"DEFAULT_FROM_NAME": default_from, "PROJECT_NAME": project_name}
        config = Settings(**config_data)
        assert config.DEFAULT_FROM_NAME == default_from

    def test_default_from_name_should_default_to_project_name(self) -> None:
        project_name = "PROJECT_NAME"
        config_data = {"PROJECT_NAME": project_name}
        config = Settings(**config_data)
        assert config.DEFAULT_FROM_NAME == project_name

    def test_emails_enabled_with_no_configuration_should_fail(self) -> None:
        config_data = {"EMAILS_ENABLED": True, "SMTP_HOST": ""}
        with pytest.raises(ValidationError):
            Settings(**config_data)
