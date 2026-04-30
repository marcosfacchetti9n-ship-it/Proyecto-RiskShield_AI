from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Transaction
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
