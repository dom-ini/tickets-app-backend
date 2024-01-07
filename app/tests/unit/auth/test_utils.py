import random
from typing import Generator

import pytest

from app.auth.utils import generate_valid_password, validate_password
from app.core.config import settings


def check_password_rules(password: str) -> bool:
    return all(rule(password) for rule in settings.PASSWORD_RULES)


@pytest.fixture(name="override_password_rules")
def do_override_password_rules() -> Generator:
    old_setting = settings.PASSWORD_RULES
    settings.PASSWORD_RULES = {lambda x: True: ""}
    yield
    settings.PASSWORD_RULES = old_setting


@pytest.fixture(name="fixed_random")
def set_random_seed() -> None:
    random.seed(0)


@pytest.mark.usefixtures("override_password_rules")
def test_validate_password_returns_password_if_all_rules_are_met() -> None:
    password = "password"
    validated = validate_password(password)
    assert validated == password


def test_validate_password_should_fail_if_rules_are_not_met() -> None:
    password = "bad"
    with pytest.raises(ValueError):
        validate_password(password)


@pytest.mark.usefixtures("fixed_random")
def test_generate_valid_password() -> None:
    for _ in range(100):
        password = generate_valid_password()
        assert check_password_rules(password)
