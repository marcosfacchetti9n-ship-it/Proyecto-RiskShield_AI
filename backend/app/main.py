from fastapi import FastAPI

from app.auth.router import router as auth_router
from app.core.config import get_settings
from app.dashboard.router import router as dashboard_router
from app.transactions.router import router as transactions_router


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="End-to-end transaction risk scoring platform.",
)

app.include_router(auth_router)
app.include_router(transactions_router)
app.include_router(dashboard_router)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.environment,
    }
