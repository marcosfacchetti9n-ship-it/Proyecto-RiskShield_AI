from app.risk.rules import evaluate_rules
from app.risk.types import Decision, RiskAssessment, RiskInput, RiskLevel, RiskModel


BASE_SCORE = 0.10
RULE_SCORE_WEIGHT = 0.60
ML_SCORE_WEIGHT = 0.40
LOW_RISK_THRESHOLD = 0.35
HIGH_RISK_THRESHOLD = 0.70


def calculate_risk(
    transaction: RiskInput,
    ml_model: RiskModel | None = None,
) -> RiskAssessment:
    rule_results = evaluate_rules(transaction)
    raw_score = BASE_SCORE + sum(rule.score_delta for rule in rule_results)
    rule_score = clamp_score(raw_score)
    ml_score = get_ml_score(transaction=transaction, ml_model=ml_model)
    model_available = ml_score is not None
    final_score = combine_scores(rule_score=rule_score, ml_score=ml_score)
    risk_level = get_risk_level(final_score)

    return RiskAssessment(
        rule_score=rule_score,
        ml_score=ml_score,
        final_score=final_score,
        risk_level=risk_level,
        decision=get_decision(risk_level),
        main_factors=[rule.factor for rule in rule_results],
        model_available=model_available,
    )


def get_ml_score(transaction: RiskInput, ml_model: RiskModel | None) -> float | None:
    if ml_model is None or not ml_model.is_available:
        return None

    score = ml_model.predict_score(transaction)
    if score is None:
        return None

    return clamp_score(score)


def combine_scores(rule_score: float, ml_score: float | None) -> float:
    if ml_score is None:
        return rule_score

    return clamp_score((RULE_SCORE_WEIGHT * rule_score) + (ML_SCORE_WEIGHT * ml_score))


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
