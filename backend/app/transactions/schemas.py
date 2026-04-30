from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


FeedbackLabel = Literal["confirmed_fraud", "false_positive", "legitimate"]


class TransactionCreate(BaseModel):
    user_id: str = Field(min_length=1, max_length=50, examples=["USR-001"])
    amount: float = Field(gt=0, examples=[250000])
    currency: str = Field(min_length=3, max_length=3, examples=["ARS"])
    country: str = Field(min_length=1, max_length=80, examples=["Argentina"])
    device: str = Field(min_length=1, max_length=50, examples=["mobile"])
    hour: int = Field(ge=0, le=23, examples=[3])
    merchant_category: str = Field(
        min_length=1,
        max_length=80,
        examples=["electronics"],
    )


class TransactionRead(TransactionCreate):
    id: int
    transaction_id: str
    rule_score: float | None = None
    ml_score: float | None = None
    final_score: float | None = None
    risk_level: str | None = None
    decision: str | None = None
    main_factors: list[str] = Field(default_factory=list)
    model_available: bool = False
    feedback_label: FeedbackLabel | None = None
    feedback_notes: str | None = None
    feedback_created_at: datetime | None = None
    feedback_updated_at: datetime | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FeedbackUpdate(BaseModel):
    feedback_label: FeedbackLabel
    feedback_notes: str | None = Field(default=None, max_length=500)
