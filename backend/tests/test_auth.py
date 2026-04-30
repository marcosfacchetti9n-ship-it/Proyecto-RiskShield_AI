from fastapi.testclient import TestClient


def register_user(client: TestClient, email: str = "admin@example.com", password: str = "StrongPass123") -> dict:
    response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )
    assert response.status_code == 201
    return response.json()


def login_user(client: TestClient, email: str = "admin@example.com", password: str = "StrongPass123") -> str:
    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )
    assert response.status_code == 200
    return str(response.json()["access_token"])


def test_register_user_successfully(client: TestClient) -> None:
    data = register_user(client)

    assert data["email"] == "admin@example.com"
    assert data["is_active"] is True
    assert "hashed_password" not in data
    assert "password" not in data


def test_register_duplicate_email_is_rejected(client: TestClient) -> None:
    register_user(client)

    response = client.post(
        "/auth/register",
        json={
            "email": "admin@example.com",
            "password": "AnotherPass123",
        },
    )

    assert response.status_code == 409


def test_login_successfully(client: TestClient) -> None:
    register_user(client)

    response = client.post(
        "/auth/login",
        json={
            "email": "admin@example.com",
            "password": "StrongPass123",
        },
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]


def test_login_with_wrong_password_fails(client: TestClient) -> None:
    register_user(client)

    response = client.post(
        "/auth/login",
        json={
            "email": "admin@example.com",
            "password": "WrongPass123",
        },
    )

    assert response.status_code == 401


def test_protected_endpoint_without_token_fails(client: TestClient) -> None:
    response = client.get("/transactions")

    assert response.status_code == 401


def test_protected_endpoint_with_valid_token_works(client: TestClient) -> None:
    register_user(client)
    token = login_user(client)

    response = client.get(
        "/transactions",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json() == []
