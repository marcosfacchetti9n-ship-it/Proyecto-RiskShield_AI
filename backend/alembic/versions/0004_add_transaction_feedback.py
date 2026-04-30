"""add transaction feedback fields

Revision ID: 0004_feedback
Revises: 0003_ml_scores
Create Date: 2026-04-30
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0004_feedback"
down_revision: Union[str, None] = "0003_ml_scores"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "transactions",
        sa.Column("feedback_label", sa.String(length=40), nullable=True),
    )
    op.add_column(
        "transactions",
        sa.Column("feedback_notes", sa.String(length=500), nullable=True),
    )
    op.add_column(
        "transactions",
        sa.Column("feedback_created_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "transactions",
        sa.Column("feedback_updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_check_constraint(
        "ck_transactions_feedback_label",
        "transactions",
        "feedback_label IS NULL OR feedback_label IN "
        "('confirmed_fraud', 'false_positive', 'legitimate')",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_transactions_feedback_label",
        "transactions",
        type_="check",
    )
    op.drop_column("transactions", "feedback_updated_at")
    op.drop_column("transactions", "feedback_created_at")
    op.drop_column("transactions", "feedback_notes")
    op.drop_column("transactions", "feedback_label")
