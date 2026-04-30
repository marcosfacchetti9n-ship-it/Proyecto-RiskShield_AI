from typing import Any

from fastapi.testclient import TestClient

from app.db.models import Transaction


def test_create_transaction_with_valid_token(
    client: TestClient,
    auth_headers: dict[str, str],
    transaction_payload: dict[str, Any],
) -> None:
    response = client.post(
        "/transactions",
        headers=auth_headers,
        json=transaction_payload,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["transaction_id"].startswith("TX-")
    assert data["user_id"] == transaction_payload["user_id"]
    assert data["amount"] == transaction_payload["amount"]


def test_create_transaction_without_token_fails(
    client: TestClient,
    transaction_payload: dict[str, Any],
) -> None:
    response = client.post("/transactions", json=transaction_payload)

    assert response.status_code == 401


def test_list_transactions_with_valid_token(
    client: TestClient,
    auth_headers: dict[str, str],
    sample_transaction: Transaction,
) -> None:
    response = client.get("/transactions", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["transaction_id"] == sample_transaction.transaction_id


def test_list_transactions_without_token_fails(client: TestClient) -> None:
    response = client.get("/transactions")

    assert response.status_code == 401


def test_create_transaction_with_invalid_payload_fails(
    client: TestClient,
    auth_headers: dict[str, str],
    transaction_payload: dict[str, Any],
) -> None:
    invalid_payload = {
        **transaction_payload,
        "amount": -100,
        "hour": 24,
    }

    response = client.post(
        "/transactions",
        headers=auth_headers,
        json=invalid_payload,
    )

    assert response.status_code == 422


def test_analyze_transaction_returns_main_factors_list(
    client: TestClient,
    auth_headers: dict[str, str],
    transaction_payload: dict[str, Any],
) -> None:
    response = client.post(
        "/transactions/analyze",
        headers=auth_headers,
        json=transaction_payload,
    )

    assert response.status_code == 201
    assert isinstance(response.json()["main_factors"], list)
