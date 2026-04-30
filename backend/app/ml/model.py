from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd

from app.core.config import get_settings
from app.risk.types import RiskInput


class MLRiskModel:
    def __init__(self, model_path: str) -> None:
        self.model_path = Path(model_path)
        self._pipeline = self._load_pipeline()

    @property
    def is_available(self) -> bool:
        return self._pipeline is not None

    def predict_score(self, transaction: RiskInput) -> float | None:
        if self._pipeline is None:
            return None

        features = pd.DataFrame(
            [
                {
                    "amount": transaction.amount,
                    "currency": transaction.currency,
                    "country": transaction.country,
                    "device": transaction.device,
                    "hour": transaction.hour,
                    "merchant_category": transaction.merchant_category,
                }
            ]
        )
        probability = self._pipeline.predict_proba(features)[0][1]
        return round(float(probability), 4)

    def _load_pipeline(self):
        if not self.model_path.exists():
            return None

        try:
            return joblib.load(self.model_path)
        except Exception:
            return None


@lru_cache
def get_ml_model() -> MLRiskModel:
    settings = get_settings()
    return MLRiskModel(model_path=settings.ml_model_path)
