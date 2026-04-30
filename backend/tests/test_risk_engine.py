from app.risk.engine import calculate_risk
from app.risk.types import RiskInput


class AvailableModel:
    def __init__(self, score: float) -> None:
        self.score = score

    @property
    def is_available(self) -> bool:
        return True

    def predict_score(self, transaction: RiskInput) -> float:
        return self.score


class UnavailableModel:
    @property
    def is_available(self) -> bool:
        return False

    def predict_score(self, transaction: RiskInput) -> float:
        return 0.99


def test_low_risk_transaction() -> None:
    assessment = calculate_risk(
        RiskInput(
            amount=5_000,
            country="Argentina",
            device="mobile",
            hour=14,
            merchant_category="groceries",
        )
    )

    assert assessment.rule_score < 0.35
    assert assessment.ml_score is None
    assert assessment.final_score < 0.35
    assert assessment.risk_level == "LOW"
    assert assessment.decision == "APPROVE"
    assert assessment.main_factors == []
    assert assessment.model_available is False


def test_medium_risk_transaction() -> None:
    assessment = calculate_risk(
        RiskInput(
            amount=150_000,
            country="Argentina",
            device="mobile",
            hour=14,
            merchant_category="electronics",
        )
    )

    assert 0.35 <= assessment.final_score <= 0.70
    assert assessment.risk_level == "MEDIUM"
    assert assessment.decision == "REVIEW"
    assert isinstance(assessment.main_factors, list)
    assert "High transaction amount" in assessment.main_factors
    assert "Moderate-risk merchant category: electronics" in assessment.main_factors


def test_high_risk_transaction() -> None:
    assessment = calculate_risk(
        RiskInput(
            amount=250_000,
            country="Argentina",
            device="unknown",
            hour=3,
            merchant_category="gambling",
        )
    )

    assert assessment.final_score > 0.70
    assert assessment.risk_level == "HIGH"
    assert assessment.decision == "BLOCK"
    assert isinstance(assessment.main_factors, list)
    assert "High-risk merchant category: gambling" in assessment.main_factors


def test_generates_score_with_available_model() -> None:
    assessment = calculate_risk(
        RiskInput(
            amount=5_000,
            country="Argentina",
            device="mobile",
            hour=14,
            merchant_category="groceries",
        ),
        ml_model=AvailableModel(score=0.90),
    )

    assert assessment.rule_score == 0.10
    assert assessment.ml_score == 0.90
    assert assessment.final_score == 0.42
    assert assessment.model_available is True


def test_falls_back_to_rules_when_model_is_unavailable() -> None:
    assessment = calculate_risk(
        RiskInput(
            amount=150_000,
            country="Argentina",
            device="mobile",
            hour=14,
            merchant_category="groceries",
        ),
        ml_model=UnavailableModel(),
    )

    assert assessment.rule_score == 0.40
    assert assessment.ml_score is None
    assert assessment.final_score == assessment.rule_score
    assert assessment.model_available is False


def test_final_score_is_always_clamped_between_zero_and_one() -> None:
    assessment = calculate_risk(
        RiskInput(
            amount=999_999_999,
            country="Brazil",
            device="unknown",
            hour=2,
            merchant_category="gambling",
            usual_country="Argentina",
        ),
        ml_model=AvailableModel(score=10.0),
    )

    assert 0.0 <= assessment.final_score <= 1.0


def test_risk_level_is_calculated_from_final_score() -> None:
    assessment = calculate_risk(
        RiskInput(
            amount=5_000,
            country="Argentina",
            device="mobile",
            hour=14,
            merchant_category="groceries",
        ),
        ml_model=AvailableModel(score=1.0),
    )

    assert assessment.rule_score == 0.10
    assert assessment.ml_score == 1.0
    assert assessment.final_score == 0.46
    assert assessment.risk_level == "MEDIUM"
    assert assessment.decision == "REVIEW"


def test_risk_engine_still_works_without_ml() -> None:
    assessment = calculate_risk(
        RiskInput(
            amount=250_000,
            country="Argentina",
            device="unknown",
            hour=3,
            merchant_category="gambling",
        )
    )

    assert assessment.ml_score is None
    assert assessment.final_score == assessment.rule_score
    assert assessment.risk_level == "HIGH"
    assert assessment.decision == "BLOCK"
