from app.risk import explanations
from app.risk.types import RiskInput, RuleResult


HIGH_AMOUNT_THRESHOLD = 100_000
SUSPICIOUS_HOUR_START = 0
SUSPICIOUS_HOUR_END = 5


def evaluate_rules(transaction: RiskInput) -> list[RuleResult]:
    results: list[RuleResult] = []

    if transaction.amount >= HIGH_AMOUNT_THRESHOLD:
        results.append(RuleResult(0.30, explanations.HIGH_AMOUNT))

    if SUSPICIOUS_HOUR_START <= transaction.hour <= SUSPICIOUS_HOUR_END:
        results.append(RuleResult(0.20, explanations.SUSPICIOUS_HOUR))

    category = transaction.merchant_category.strip().lower()
    if category == "electronics":
        results.append(RuleResult(0.15, explanations.ELECTRONICS_CATEGORY))
    elif category == "gambling":
        results.append(RuleResult(0.35, explanations.GAMBLING_CATEGORY))

    if transaction.device.strip().lower() == "unknown":
        results.append(RuleResult(0.15, explanations.UNKNOWN_DEVICE))

    if _has_country_mismatch(
        country=transaction.country,
        usual_country=transaction.usual_country,
    ):
        results.append(RuleResult(0.20, explanations.UNUSUAL_COUNTRY))

    return results


def _has_country_mismatch(country: str, usual_country: str | None) -> bool:
    if not usual_country:
        return False

    return country.strip().lower() != usual_country.strip().lower()
