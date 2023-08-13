from fastapi.testclient import TestClient

from app.core.config import settings


def _get_token_headers(client: TestClient, login_data: dict[str, str]) -> dict[str, str]:
    request = client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)
    tokens = request.json()
    access_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    return headers


def get_superuser_token_headers(client: TestClient) -> dict[str, str]:
    login_data = {"username": settings.TEST_SUPERUSER_EMAIL, "password": settings.TEST_SUPERUSER_PASSWORD}
    return _get_token_headers(client, login_data)


def get_normal_user_token_headers(client: TestClient) -> dict[str, str]:
    login_data = {"username": settings.TEST_USER_EMAIL, "password": settings.TEST_USER_PASSWORD}
    return _get_token_headers(client, login_data)
