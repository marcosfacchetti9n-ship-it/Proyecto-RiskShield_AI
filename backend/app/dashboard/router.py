from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.service import get_current_active_user
from app.dashboard import service
from app.dashboard.schemas import (
    CategoryRiskSummary,
    CountryRiskSummary,
    DashboardMetrics,
    RecentTransaction,
)
from app.db.session import get_db


router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"],
    dependencies=[Depends(get_current_active_user)],
)


@router.get("/metrics", response_model=DashboardMetrics)
def get_metrics(db: Session = Depends(get_db)) -> DashboardMetrics:
    return service.get_dashboard_metrics(db=db)


@router.get("/recent-transactions", response_model=list[RecentTransaction])
def get_recent_transactions(
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
) -> list[RecentTransaction]:
    return service.get_recent_transactions(db=db, limit=limit)


@router.get("/country-risk", response_model=list[CountryRiskSummary])
def get_country_risk(db: Session = Depends(get_db)) -> list[CountryRiskSummary]:
    return service.get_country_risk(db=db)


@router.get("/category-risk", response_model=list[CategoryRiskSummary])
def get_category_risk(db: Session = Depends(get_db)) -> list[CategoryRiskSummary]:
    return service.get_category_risk(db=db)
