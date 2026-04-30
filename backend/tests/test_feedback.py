from datetime import datetime, timezone
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Transaction


def get_auth_headers(client: TestClient) -> dict[str, str]:
    credentials = {
        "email": "feedback-admin@example.com",
        "password": "StrongPass123",
    }
    register_response = client.post("/auth/register", json=credentials)
    assert register_response.status_code == 201

    login_response = client.post("/auth/login", json=credentials)
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def add_transaction(db: Session, transaction_id: str) -> Transaction:
    transaction = Transaction(
        transaction_id=transaction_id,
        user_id="USR-FEEDBACK",
        amount=Decimal("1500.00"),
        currency="ARS",
        country="Argentina",
        device="mobile",
        hour=14,
        merchant_category="groceries",
        rule_score=Decimal("0.2000"),
        ml_score=None,
        risk_score=Decimal("0.2000"),
        risk_level="LOW",
        decision="APPROVE",
        model_available=False,
        main_factors=[],
        created_at=datetime.now(timezone.utc),
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


def test_feedback_without_token_fails(client: TestClient, db_session: Session) -> None:
    add_transaction(db_session, transaction_id="TX-FEEDBACK-NO-TOKEN")

    response = client.patch(
        "/transactions/TX-FEEDBACK-NO-TOKEN/feedback",
        json={
            "feedback_label": "confirmed_fraud",
            "feedback_notes": "Confirmed after manual review.",
        },
    )

    assert response.status_code == 401


def test_feedback_with_valid_token_updates_transaction(
    client: TestClient,
    db_session: Session,
) -> None:
    headers = get_auth_headers(client)
    add_transaction(db_session, transaction_id="TX-FEEDBACK-VALID")

    response = client.patch(
        "/transactions/TX-FEEDBACK-VALID/feedback",
        headers=headers,
        json={
            "feedback_label": "confirmed_fraud",
            "feedback_notes": "Confirmed after manual review.",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["feedback_label"] == "confirmed_fraud"
    assert data["feedback_notes"] == "Confirmed after manual review."
    assert data["feedback_created_at"] is not None
    assert data["feedback_updated_at"] is not None


def test_feedback_invalid_label_fails(client: TestClient, db_session: Session) -> None:
    headers = get_auth_headers(client)
    add_transaction(db_session, transaction_id="TX-FEEDBACK-INVALID")

    response = client.patch(
        "/transactions/TX-FEEDBACK-INVALID/feedback",
        headers=headers,
        json={
            "feedback_label": "not_a_valid_label",
            "feedback_notes": "Invalid label.",
        },
    )

    assert response.status_code == 422


def test_feedback_missing_transaction_returns_404(client: TestClient) -> None:
    headers = get_auth_headers(client)

    response = client.patch(
        "/transactions/TX-DOES-NOT-EXIST/feedback",
        headers=headers,
        json={
            "feedback_label": "false_positive",
            "feedback_notes": "Manual review overturned the decision.",
        },
    )

    assert response.status_code == 404


def test_feedback_is_persisted(client: TestClient, db_session: Session) -> None:
    headers = get_auth_headers(client)
    add_transaction(db_session, transaction_id="TX-FEEDBACK-PERSISTED")

    response = client.patch(
        "/transactions/TX-FEEDBACK-PERSISTED/feedback",
        headers=headers,
        json={
            "feedback_label": "legitimate",
            "feedback_notes": "Customer confirmed the purchase.",
        },
    )

    assert response.status_code == 200

    db_session.expire_all()
    transaction = db_session.scalars(
        select(Transaction).where(Transaction.transaction_id == "TX-FEEDBACK-PERSISTED")
    ).first()
    assert transaction is not None
    assert transaction.feedback_label == "legitimate"
    assert transaction.feedback_notes == "Customer confirmed the purchase."
    assert transaction.feedback_created_at is not None
    assert transaction.feedback_updated_at is not None


def test_dashboard_metrics_include_feedback_counts(
    client: TestClient,
    db_session: Session,
) -> None:
    headers = get_auth_headers(client)
    add_transaction(db_session, transaction_id="TX-FEEDBACK-METRICS-001")
    confirmed = add_transaction(db_session, transaction_id="TX-FEEDBACK-METRICS-002")
    false_positive = add_transaction(db_session, transaction_id="TX-FEEDBACK-METRICS-003")
    legitimate = add_transaction(db_session, transaction_id="TX-FEEDBACK-METRICS-004")
    confirmed.feedback_label = "confirmed_fraud"
    false_positive.feedback_label = "false_positive"
    legitimate.feedback_label = "legitimate"
    db_session.commit()

    response = client.get("/dashboard/metrics", headers=headers)

    assert response.status_code == 200
    assert response.json()["feedback_counts"] == {
        "confirmed_fraud": 1,
        "false_positive": 1,
        "legitimate": 1,
        "unreviewed": 1,
    }
