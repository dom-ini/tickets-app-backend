import logging

from app.loggers import create_stdout_handler, set_up_logger


def test_create_stdout_handler_creates_stream_handler() -> None:
    handler = create_stdout_handler()
    assert isinstance(handler, logging.StreamHandler)


def test_create_stdout_handler_creates_valid_formatter() -> None:
    handler = create_stdout_handler()
    formatter = handler.formatter
    assert isinstance(formatter, logging.Formatter)
    fields = ["asctime", "levelname", "message"]
    assert all(field in str(formatter._fmt) for field in fields)  # pylint: disable=W0212


def test_set_up_logger_should_set_name() -> None:
    logger_name = "test_logger"
    logger = set_up_logger(logger_name)
    assert logger.name == logger_name


def test_set_up_logger_should_set_info_level() -> None:
    logger_name = "test_logger"
    logger = set_up_logger(logger_name)
    assert logger.level == logging.INFO


def test_set_up_logger_should_set_stream_handler() -> None:
    logger_name = "test_logger"
    logger = set_up_logger(logger_name)
    assert any(isinstance(handler, logging.StreamHandler) for handler in logger.handlers)
