from unittest.mock import AsyncMock, Mock

import pytest
from pytest_mock import MockerFixture

from app.common.emails import MailSender, get_mailer_config, mailer, prepare_email, read_template

EMAIL_TEMPLATE_NAME = "base.html"


@pytest.fixture(name="mock_mail_engine")
def get_mock_mail_engine() -> Mock:
    return Mock()


def test_mailer() -> None:
    mail_sender = mailer()
    assert mail_sender is not None
    assert hasattr(mail_sender, "engine")


@pytest.mark.asyncio
async def test_mail_sender_send() -> None:
    async_mail_engine_mock = AsyncMock()
    mail_sender = MailSender(async_mail_engine_mock)
    message = ""

    await mail_sender.send(message)
    async_mail_engine_mock.send_message.assert_called_once_with(message)


def test_mail_sender_record_messages(mock_mail_engine: Mock, mocker: MockerFixture) -> None:
    outbox = "test"
    mock_record_messages = mocker.patch.object(mock_mail_engine, "record_messages")
    mock_record_messages.return_value.__enter__.return_value = outbox
    mail_sender = MailSender(mock_mail_engine)

    with mail_sender.record_messages() as result:
        assert result == outbox


def test_read_template() -> None:
    template_name = EMAIL_TEMPLATE_NAME
    template = read_template(template_name)
    assert isinstance(template, str)


def test_read_template_with_incorrect_template_name_should_raise_error() -> None:
    template_name = "non-existing-template"
    with pytest.raises(FileNotFoundError):
        read_template(template_name)


def test_prepare_email_mail_should_have_correct_attributes() -> None:
    recipients = ["random@example.com"]
    subject = "subject"
    mail = prepare_email(email_to=recipients, subject=subject, template_name=EMAIL_TEMPLATE_NAME)
    assert hasattr(mail, "body")
    assert mail.subject == subject
    assert set(mail.recipients) == set(recipients)


def test_get_mailer_config_should_return_prefixed_keys() -> None:
    config = get_mailer_config()
    assert all(key.startswith("MAIL") for key in config)
