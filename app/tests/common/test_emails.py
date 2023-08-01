from app.common.emails import mailer


class TestEmails:
    def test_mailer(self) -> None:
        mail_sender = mailer()
        assert mail_sender is not None
        assert hasattr(mail_sender, "engine")
