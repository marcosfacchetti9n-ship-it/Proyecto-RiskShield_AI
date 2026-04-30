"""add ml score fields

Revision ID: 0003_ml_scores
Revises: 0002_main_factors
Create Date: 2026-04-30
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0003_ml_scores"
down_revision: Union[str, None] = "0002_main_factors"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "transactions",
        sa.Column("rule_score", sa.Numeric(precision=5, scale=4), nullable=True),
    )
    op.add_column(
        "transactions",
        sa.Column("ml_score", sa.Numeric(precision=5, scale=4), nullable=True),
    )
    op.add_column(
        "transactions",
        sa.Column(
            "model_available",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("transactions", "model_available")
    op.drop_column("transactions", "ml_score")
    op.drop_column("transactions", "rule_score")
