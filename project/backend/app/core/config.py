"""Application configuration management via environment variables."""

from typing import List, Union

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application runtime settings."""

    PROJECT_NAME: str = "Coffee Shop Online Ordering API"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"

    # Security & Authentication
    SECRET_KEY: str = "dev-insecure-secret-key-change-in-production-1234567890"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Initial Superuser Provisioning (Optional, via environment)
    FIRST_SUPERUSER_EMAIL: str = ""
    FIRST_SUPERUSER_PASSWORD: str = ""

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/coffeeshop"

    # CORS
    BACKEND_CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
    ]

    @field_validator("BACKEND_CORS_ORIGINS")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return [str(i) for i in v]
        raise ValueError(v)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
