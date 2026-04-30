from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, DateTime, Integer, JSON, Numeric, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_transactions_amount_positive"),
        CheckConstraint("hour >= 0 AND hour <= 23", name="ck_transactions_hour_range"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    transaction_id: Mapped[str] = mapped_column(
        String(40),
        unique=True,
        index=True,
        nullable=False,
    )
    user_id: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    country: Mapped[str] = mapped_column(String(80), nullable=False)
    device: Mapped[str] = mapped_column(String(50), nullable=False)
    hour: Mapped[int] = mapped_column(Integer, nullable=False)
    merchant_category: Mapped[str] = mapped_column(String(80), nullable=False)
    rule_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 4), nullable=True)
    ml_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 4), nullable=True)
    risk_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 4), nullable=True)
    risk_level: Mapped[str | None] = mapped_column(String(20), nullable=True)
    decision: Mapped[str | None] = mapped_column(String(20), nullable=True)
    model_available: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=text("false"),
        nullable=False,
    )
    main_factors: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        server_default=text("'[]'::json"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    @property
    def final_score(self) -> Decimal | None:
        return self.risk_score
