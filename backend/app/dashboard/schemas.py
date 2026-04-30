from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DashboardMetrics(BaseModel):
    total_transactions: int
    risk_level_counts: dict[str, int]
    decision_counts: dict[str, int]
    blocked_rate: float
    average_final_score: float
    model_available_rate: float
    feedback_counts: dict[str, int]


class RecentTransaction(BaseModel):
    id: int
    transaction_id: str
    user_id: str
    amount: float
    currency: str
    country: str
    merchant_category: str
    risk_level: str | None = None
    decision: str | None = None
    final_score: float | None = None
    feedback_label: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CountryRiskSummary(BaseModel):
    country: str
    total_transactions: int
    high_risk_transactions: int
    blocked_transactions: int
    average_score: float


class CategoryRiskSummary(BaseModel):
    merchant_category: str
    total_transactions: int
    high_risk_transactions: int
    blocked_transactions: int
    average_score: float
