from sqlalchemy import case, desc, func, select
from sqlalchemy.orm import Session

from app.dashboard.schemas import CategoryRiskSummary, CountryRiskSummary, DashboardMetrics
from app.db.models import Transaction


RISK_LEVELS = ("LOW", "MEDIUM", "HIGH")
DECISIONS = ("APPROVE", "REVIEW", "BLOCK")
FEEDBACK_LABELS = ("confirmed_fraud", "false_positive", "legitimate")


def get_dashboard_metrics(db: Session) -> DashboardMetrics:
    total_transactions = db.scalar(select(func.count(Transaction.id))) or 0
    risk_level_counts = _get_group_counts(db=db, column=Transaction.risk_level, keys=RISK_LEVELS)
    decision_counts = _get_group_counts(db=db, column=Transaction.decision, keys=DECISIONS)
    feedback_counts = _get_feedback_counts(db=db)

    if total_transactions == 0:
        return DashboardMetrics(
            total_transactions=0,
            risk_level_counts=risk_level_counts,
            decision_counts=decision_counts,
            blocked_rate=0.0,
            average_final_score=0.0,
            model_available_rate=0.0,
            feedback_counts=feedback_counts,
        )

    blocked_transactions = decision_counts["BLOCK"]
    average_score = db.scalar(select(func.avg(Transaction.risk_score))) or 0
    model_available_count = (
        db.scalar(
            select(func.count(Transaction.id)).where(Transaction.model_available.is_(True))
        )
        or 0
    )

    return DashboardMetrics(
        total_transactions=total_transactions,
        risk_level_counts=risk_level_counts,
        decision_counts=decision_counts,
        blocked_rate=_round_ratio(blocked_transactions, total_transactions),
        average_final_score=round(float(average_score), 4),
        model_available_rate=_round_ratio(model_available_count, total_transactions),
        feedback_counts=feedback_counts,
    )


def get_recent_transactions(db: Session, limit: int = 10) -> list[Transaction]:
    statement = select(Transaction).order_by(Transaction.created_at.desc()).limit(limit)
    return list(db.scalars(statement).all())


def get_country_risk(db: Session) -> list[CountryRiskSummary]:
    rows = _get_grouped_risk_rows(db=db, group_column=Transaction.country)
    return [
        CountryRiskSummary(
            country=str(row.group_key),
            total_transactions=row.total_transactions,
            high_risk_transactions=row.high_risk_transactions,
            blocked_transactions=row.blocked_transactions,
            average_score=round(float(row.average_score or 0), 4),
        )
        for row in rows
    ]


def get_category_risk(db: Session) -> list[CategoryRiskSummary]:
    rows = _get_grouped_risk_rows(db=db, group_column=Transaction.merchant_category)
    return [
        CategoryRiskSummary(
            merchant_category=str(row.group_key),
            total_transactions=row.total_transactions,
            high_risk_transactions=row.high_risk_transactions,
            blocked_transactions=row.blocked_transactions,
            average_score=round(float(row.average_score or 0), 4),
        )
        for row in rows
    ]


def _get_group_counts(db: Session, column, keys: tuple[str, ...]) -> dict[str, int]:
    counts = {key: 0 for key in keys}
    rows = db.execute(select(column, func.count(Transaction.id)).group_by(column)).all()

    for key, count in rows:
        if key in counts:
            counts[str(key)] = int(count)

    return counts


def _get_feedback_counts(db: Session) -> dict[str, int]:
    counts = {key: 0 for key in FEEDBACK_LABELS}
    counts["unreviewed"] = 0
    rows = db.execute(
        select(Transaction.feedback_label, func.count(Transaction.id)).group_by(
            Transaction.feedback_label
        )
    ).all()

    for label, count in rows:
        if label is None:
            counts["unreviewed"] = int(count)
        elif label in counts:
            counts[str(label)] = int(count)

    return counts


def _get_grouped_risk_rows(db: Session, group_column):
    high_risk_count = func.sum(
        case((Transaction.risk_level == "HIGH", 1), else_=0)
    ).label("high_risk_transactions")
    blocked_count = func.sum(
        case((Transaction.decision == "BLOCK", 1), else_=0)
    ).label("blocked_transactions")
    total_count = func.count(Transaction.id).label("total_transactions")
    average_score = func.avg(Transaction.risk_score).label("average_score")

    statement = (
        select(
            group_column.label("group_key"),
            total_count,
            high_risk_count,
            blocked_count,
            average_score,
        )
        .group_by(group_column)
        .order_by(desc(total_count))
    )

    return db.execute(statement).all()


def _round_ratio(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0

    return round(numerator / denominator, 4)
