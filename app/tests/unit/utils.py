from app.auth.models import User


def create_user_instance(email: str = "email@example.com") -> User:
    payload = {
        "email": email,
        "hashed_password": "hash",
    }
    user = User(**payload)
    return user
