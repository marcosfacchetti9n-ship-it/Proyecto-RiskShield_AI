import os
from collections.abc import Generator
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Callable

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

os.environ.setdefault("SECRET_KEY", "test-secret-key-with-at-least-thirty-two-chars")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "60")

from app.db.database import Base
from app.db.models import Transaction
from app.db.session import get_db
from app.main import app


engine = create_engine(
    "sqlite+pysqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture()
def db_session(client: TestClient) -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def admin_credentials() -> dict[str, str]:
    return {
        "email": "admin@example.com",
        "password": "StrongPass123",
    }


@pytest.fixture()
def admin_user(
    client: TestClient,
    admin_credentials: dict[str, str],
) -> dict[str, Any]:
    response = client.post("/auth/register", json=admin_credentials)
    assert response.status_code == 201
    return dict(response.json())


@pytest.fixture()
def auth_token(
    client: TestClient,
    admin_user: dict[str, Any],
    admin_credentials: dict[str, str],
) -> str:
    response = client.post("/auth/login", json=admin_credentials)
    assert response.status_code == 200
    return str(response.json()["access_token"])


@pytest.fixture()
def auth_headers(auth_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture()
def transaction_payload() -> dict[str, Any]:
    return {
        "user_id": "USR-001",
        "amount": 250000,
        "currency": "ARS",
        "country": "Argentina",
        "device": "mobile",
        "hour": 3,
        "merchant_category": "electronics",
    }


@pytest.fixture()
def transaction_factory(db_session: Session) -> Callable[..., Transaction]:
    def create_transaction(
        transaction_id: str = "TX-TEST-001",
        user_id: str = "USR-TEST",
        amount: Decimal = Decimal("1000.00"),
        currency: str = "ARS",
        country: str = "Argentina",
        device: str = "mobile",
        hour: int = 12,
        merchant_category: str = "groceries",
        rule_score: Decimal | None = Decimal("0.2000"),
        ml_score: Decimal | None = None,
        risk_score: Decimal | None = Decimal("0.2000"),
        risk_level: str | None = "LOW",
        decision: str | None = "APPROVE",
        model_available: bool = False,
        main_factors: list[str] | None = None,
        feedback_label: str | None = None,
        feedback_notes: str | None = None,
        created_at: datetime | None = None,
    ) -> Transaction:
        transaction = Transaction(
            transaction_id=transaction_id,
            user_id=user_id,
            amount=amount,
            currency=currency,
            country=country,
            device=device,
            hour=hour,
            merchant_category=merchant_category,
            rule_score=rule_score,
            ml_score=ml_score,
            risk_score=risk_score,
            risk_level=risk_level,
            decision=decision,
            model_available=model_available,
            main_factors=main_factors or [],
            feedback_label=feedback_label,
            feedback_notes=feedback_notes,
            created_at=created_at or datetime.now(timezone.utc),
        )
        db_session.add(transaction)
        db_session.commit()
        db_session.refresh(transaction)
        return transaction

    return create_transaction


@pytest.fixture()
def sample_transaction(
    transaction_factory: Callable[..., Transaction],
) -> Transaction:
    return transaction_factory()
