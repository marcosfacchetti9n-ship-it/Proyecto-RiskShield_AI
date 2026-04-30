from app.risk.rules import evaluate_rules
from app.risk.types import Decision, RiskAssessment, RiskInput, RiskLevel


BASE_SCORE = 0.10
LOW_RISK_THRESHOLD = 0.35
HIGH_RISK_THRESHOLD = 0.70


def calculate_risk(transaction: RiskInput) -> RiskAssessment:
    rule_results = evaluate_rules(transaction)
    raw_score = BASE_SCORE + sum(rule.score_delta for rule in rule_results)
    risk_score = clamp_score(raw_score)
    risk_level = get_risk_level(risk_score)

    return RiskAssessment(
        risk_score=risk_score,
        risk_level=risk_level,
        decision=get_decision(risk_level),
        main_factors=[rule.factor for rule in rule_results],
    )


def clamp_score(score: float) -> float:
    return round(min(max(score, 0.0), 1.0), 4)


def get_risk_level(score: float) -> RiskLevel:
    if score < LOW_RISK_THRESHOLD:
        return "LOW"

    if score <= HIGH_RISK_THRESHOLD:
        return "MEDIUM"

    return "HIGH"


def get_decision(risk_level: RiskLevel) -> Decision:
    decisions: dict[RiskLevel, Decision] = {
        "LOW": "APPROVE",
        "MEDIUM": "REVIEW",
        "HIGH": "BLOCK",
    }

    return decisions[risk_level]
