from uuid import uuid4

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.db.models import Transaction
from app.risk.engine import calculate_risk
from app.risk.types import RiskInput
from app.transactions.schemas import TransactionCreate


def create_transaction(
    db: Session,
    transaction_in: TransactionCreate,
) -> Transaction:
    transaction = Transaction(
        transaction_id=f"TX-{uuid4().hex[:12].upper()}",
        **transaction_in.model_dump(),
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return transaction


def analyze_transaction(
    db: Session,
    transaction_in: TransactionCreate,
) -> Transaction:
    usual_country = get_usual_country(db=db, user_id=transaction_in.user_id)
    risk_input = RiskInput(
        amount=transaction_in.amount,
        country=transaction_in.country,
        device=transaction_in.device,
        hour=transaction_in.hour,
        merchant_category=transaction_in.merchant_category,
        usual_country=usual_country,
    )
    assessment = calculate_risk(risk_input)

    transaction = Transaction(
        transaction_id=f"TX-{uuid4().hex[:12].upper()}",
        risk_score=assessment.risk_score,
        risk_level=assessment.risk_level,
        decision=assessment.decision,
        main_factors=assessment.main_factors,
        **transaction_in.model_dump(),
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return transaction


def list_transactions(
    db: Session,
    limit: int = 50,
    offset: int = 0,
) -> list[Transaction]:
    statement = (
        select(Transaction)
        .order_by(Transaction.created_at.desc())
        .offset(offset)
        .limit(limit)
    )

    return list(db.scalars(statement).all())


def get_usual_country(db: Session, user_id: str) -> str | None:
    count_label = func.count(Transaction.id).label("transaction_count")
    statement = (
        select(Transaction.country, count_label)
        .where(Transaction.user_id == user_id)
        .group_by(Transaction.country)
        .order_by(desc(count_label))
        .limit(1)
    )
    result = db.execute(statement).first()

    if result is None:
        return None

    return str(result[0])
