import logging as log
import sys


def create_stdout_handler() -> log.Handler:
    handler = log.StreamHandler(sys.stdout)
    formatter = log.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    return handler


def set_up_logger(name: str) -> log.Logger:
    new_logger = log.getLogger(name)
    new_logger.setLevel(log.INFO)
    handler = create_stdout_handler()
    new_logger.addHandler(handler)
    return new_logger


logger = set_up_logger(__name__)
