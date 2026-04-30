from fastapi.testclient import TestClient


def test_register_user_successfully(
    client: TestClient,
    admin_credentials: dict[str, str],
) -> None:
    response = client.post(
        "/auth/register",
        json=admin_credentials,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "admin@example.com"
    assert data["is_active"] is True
    assert "hashed_password" not in data
    assert "password" not in data


def test_register_duplicate_email_is_rejected(
    client: TestClient,
    admin_user: dict,
) -> None:
    response = client.post(
        "/auth/register",
        json={
            "email": "admin@example.com",
            "password": "AnotherPass123",
        },
    )

    assert response.status_code == 409


def test_login_successfully(
    client: TestClient,
    admin_user: dict,
    admin_credentials: dict[str, str],
) -> None:
    response = client.post(
        "/auth/login",
        json=admin_credentials,
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]


def test_login_with_invalid_credentials_fails(
    client: TestClient,
    admin_user: dict,
) -> None:
    response = client.post(
        "/auth/login",
        json={
            "email": "admin@example.com",
            "password": "WrongPass123",
        },
    )

    assert response.status_code == 401


def test_auth_me_without_token_fails(client: TestClient) -> None:
    response = client.get("/auth/me")

    assert response.status_code == 401


def test_auth_me_with_valid_token_works(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = client.get("/auth/me", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "admin@example.com"
    assert data["is_active"] is True
