import logging
import sys


def create_stdout_handler() -> logging.Handler:
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    return handler


def set_up_logger(name: str) -> logging.Logger:
    new_logger = logging.getLogger(name)
    new_logger.setLevel(logging.INFO)
    handler = create_stdout_handler()
    new_logger.addHandler(handler)
    return new_logger


logger = set_up_logger(__name__)
