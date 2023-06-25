import random
import string

from app.core.config import settings


def validate_password(password: str) -> str:
    for rule, error_msg in settings.PASSWORD_RULES.items():
        if not rule(password):
            raise ValueError(error_msg)
    return password


def generate_valid_password() -> str:
    uppercase = string.ascii_uppercase
    lowercase = string.ascii_lowercase
    digits = string.digits
    special = string.punctuation
    full = uppercase + lowercase + digits + special
    password = ""
    target_length = settings.PASSWORD_MIN_LENGTH + random.randint(0, 8)
    for charset in (uppercase, lowercase, digits, special):
        password += random.choice(charset)
    while len(password) < target_length:
        password += random.choice(full)

    return password
