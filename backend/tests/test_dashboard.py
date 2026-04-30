from datetime import datetime, timedelta, timezone
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.models import Transaction


def get_auth_headers(client: TestClient) -> dict[str, str]:
    credentials = {
        "email": "dashboard-admin@example.com",
        "password": "StrongPass123",
    }
    register_response = client.post("/auth/register", json=credentials)
    assert register_response.status_code == 201

    login_response = client.post("/auth/login", json=credentials)
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def add_transaction(
    db: Session,
    transaction_id: str,
    country: str = "Argentina",
    merchant_category: str = "groceries",
    risk_level: str | None = "LOW",
    decision: str | None = "APPROVE",
    risk_score: Decimal | None = Decimal("0.2000"),
    model_available: bool = False,
    feedback_label: str | None = None,
    feedback_notes: str | None = None,
    created_at: datetime | None = None,
) -> Transaction:
    transaction = Transaction(
        transaction_id=transaction_id,
        user_id="USR-DASH",
        amount=Decimal("1000.00"),
        currency="ARS",
        country=country,
        device="mobile",
        hour=12,
        merchant_category=merchant_category,
        rule_score=risk_score,
        ml_score=None,
        risk_score=risk_score,
        risk_level=risk_level,
        decision=decision,
        model_available=model_available,
        main_factors=[],
        feedback_label=feedback_label,
        feedback_notes=feedback_notes,
        created_at=created_at or datetime.now(timezone.utc),
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


def test_dashboard_without_token_fails(client: TestClient) -> None:
    response = client.get("/dashboard/metrics")

    assert response.status_code == 401


def test_dashboard_with_valid_token_works(client: TestClient) -> None:
    headers = get_auth_headers(client)

    response = client.get("/dashboard/metrics", headers=headers)

    assert response.status_code == 200
    assert response.json()["total_transactions"] == 0


def test_metrics_with_empty_database_do_not_break(client: TestClient) -> None:
    headers = get_auth_headers(client)

    response = client.get("/dashboard/metrics", headers=headers)

    assert response.status_code == 200
    assert response.json() == {
        "total_transactions": 0,
        "risk_level_counts": {"LOW": 0, "MEDIUM": 0, "HIGH": 0},
        "decision_counts": {"APPROVE": 0, "REVIEW": 0, "BLOCK": 0},
        "blocked_rate": 0.0,
        "average_final_score": 0.0,
        "model_available_rate": 0.0,
        "feedback_counts": {
            "confirmed_fraud": 0,
            "false_positive": 0,
            "legitimate": 0,
            "unreviewed": 0,
        },
    }


def test_metrics_calculate_total_transactions(client: TestClient, db_session: Session) -> None:
    headers = get_auth_headers(client)
    add_transaction(db_session, transaction_id="TX-DASH-001")
    add_transaction(
        db_session,
        transaction_id="TX-DASH-002",
        risk_level="MEDIUM",
        decision="REVIEW",
        risk_score=Decimal("0.5000"),
        model_available=True,
    )
    add_transaction(
        db_session,
        transaction_id="TX-DASH-003",
        risk_level="HIGH",
        decision="BLOCK",
        risk_score=Decimal("0.9000"),
        feedback_label="confirmed_fraud",
    )

    response = client.get("/dashboard/metrics", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["total_transactions"] == 3
    assert data["risk_level_counts"] == {"LOW": 1, "MEDIUM": 1, "HIGH": 1}
    assert data["decision_counts"] == {"APPROVE": 1, "REVIEW": 1, "BLOCK": 1}
    assert data["blocked_rate"] == 0.3333
    assert data["average_final_score"] == 0.5333
    assert data["model_available_rate"] == 0.3333
    assert data["feedback_counts"] == {
        "confirmed_fraud": 1,
        "false_positive": 0,
        "legitimate": 0,
        "unreviewed": 2,
    }


def test_recent_transactions_respects_limit(client: TestClient, db_session: Session) -> None:
    headers = get_auth_headers(client)
    base_time = datetime.now(timezone.utc)
    add_transaction(db_session, transaction_id="TX-RECENT-001", created_at=base_time)
    add_transaction(
        db_session,
        transaction_id="TX-RECENT-002",
        created_at=base_time + timedelta(minutes=1),
    )
    add_transaction(
        db_session,
        transaction_id="TX-RECENT-003",
        created_at=base_time + timedelta(minutes=2),
    )

    response = client.get("/dashboard/recent-transactions?limit=2", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["transaction_id"] == "TX-RECENT-003"
    assert data[1]["transaction_id"] == "TX-RECENT-002"


def test_country_risk_groups_transactions(client: TestClient, db_session: Session) -> None:
    headers = get_auth_headers(client)
    add_transaction(
        db_session,
        transaction_id="TX-COUNTRY-001",
        country="Argentina",
        risk_score=Decimal("0.2000"),
    )
    add_transaction(
        db_session,
        transaction_id="TX-COUNTRY-002",
        country="Argentina",
        risk_level="HIGH",
        decision="BLOCK",
        risk_score=Decimal("0.8000"),
    )
    add_transaction(
        db_session,
        transaction_id="TX-COUNTRY-003",
        country="Brazil",
        risk_level="HIGH",
        decision="BLOCK",
        risk_score=Decimal("0.9000"),
    )

    response = client.get("/dashboard/country-risk", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data[0] == {
        "country": "Argentina",
        "total_transactions": 2,
        "high_risk_transactions": 1,
        "blocked_transactions": 1,
        "average_score": 0.5,
    }
    assert data[1]["country"] == "Brazil"
    assert data[1]["total_transactions"] == 1


def test_category_risk_groups_transactions(client: TestClient, db_session: Session) -> None:
    headers = get_auth_headers(client)
    add_transaction(
        db_session,
        transaction_id="TX-CATEGORY-001",
        merchant_category="electronics",
        risk_score=Decimal("0.4000"),
    )
    add_transaction(
        db_session,
        transaction_id="TX-CATEGORY-002",
        merchant_category="electronics",
        risk_level="HIGH",
        decision="BLOCK",
        risk_score=Decimal("0.8000"),
    )
    add_transaction(
        db_session,
        transaction_id="TX-CATEGORY-003",
        merchant_category="travel",
        risk_level="MEDIUM",
        decision="REVIEW",
        risk_score=Decimal("0.5000"),
    )

    response = client.get("/dashboard/category-risk", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data[0] == {
        "merchant_category": "electronics",
        "total_transactions": 2,
        "high_risk_transactions": 1,
        "blocked_transactions": 1,
        "average_score": 0.6,
    }
    assert data[1]["merchant_category"] == "travel"
    assert data[1]["total_transactions"] == 1
