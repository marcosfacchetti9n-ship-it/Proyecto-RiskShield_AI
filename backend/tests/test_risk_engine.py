from app.risk.engine import calculate_risk
from app.risk.types import RiskInput


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

    assert assessment.risk_score < 0.35
    assert assessment.risk_level == "LOW"
    assert assessment.decision == "APPROVE"
    assert assessment.main_factors == []


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

    assert 0.35 <= assessment.risk_score <= 0.70
    assert assessment.risk_level == "MEDIUM"
    assert assessment.decision == "REVIEW"
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

    assert assessment.risk_score > 0.70
    assert assessment.risk_level == "HIGH"
    assert assessment.decision == "BLOCK"
    assert "High-risk merchant category: gambling" in assessment.main_factors


def test_score_is_always_clamped_between_zero_and_one() -> None:
    assessment = calculate_risk(
        RiskInput(
            amount=999_999_999,
            country="Brazil",
            device="unknown",
            hour=2,
            merchant_category="gambling",
            usual_country="Argentina",
        )
    )

    assert 0.0 <= assessment.risk_score <= 1.0
