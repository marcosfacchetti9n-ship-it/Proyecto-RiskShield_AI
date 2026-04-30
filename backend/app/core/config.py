from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "RiskShield AI"
    environment: str = "development"
    database_url: str = (
        "postgresql+psycopg://riskshield:riskshield_password@localhost:5432/riskshield_ai"
    )
    ml_model_path: str = "app/ml/model.joblib"
    secret_key: str = Field(min_length=32)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
