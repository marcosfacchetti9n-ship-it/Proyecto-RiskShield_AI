from dataclasses import dataclass
from typing import Literal


RiskLevel = Literal["LOW", "MEDIUM", "HIGH"]
Decision = Literal["APPROVE", "REVIEW", "BLOCK"]


@dataclass(frozen=True)
class RiskInput:
    amount: float
    country: str
    device: str
    hour: int
    merchant_category: str
    usual_country: str | None = None


@dataclass(frozen=True)
class RuleResult:
    score_delta: float
    factor: str


@dataclass(frozen=True)
class RiskAssessment:
    risk_score: float
    risk_level: RiskLevel
    decision: Decision
    main_factors: list[str]
