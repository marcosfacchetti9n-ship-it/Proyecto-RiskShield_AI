from dataclasses import dataclass
from typing import Literal, Protocol


RiskLevel = Literal["LOW", "MEDIUM", "HIGH"]
Decision = Literal["APPROVE", "REVIEW", "BLOCK"]


@dataclass(frozen=True)
class RiskInput:
    amount: float
    country: str
    device: str
    hour: int
    merchant_category: str
    currency: str = "ARS"
    usual_country: str | None = None


@dataclass(frozen=True)
class RuleResult:
    score_delta: float
    factor: str


@dataclass(frozen=True)
class RiskAssessment:
    rule_score: float
    ml_score: float | None
    final_score: float
    risk_level: RiskLevel
    decision: Decision
    main_factors: list[str]
    model_available: bool

    @property
    def risk_score(self) -> float:
        return self.final_score


class RiskModel(Protocol):
    @property
    def is_available(self) -> bool:
        pass

    def predict_score(self, transaction: RiskInput) -> float | None:
        pass
