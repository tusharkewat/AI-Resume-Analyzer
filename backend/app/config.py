import os
import logging
from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, model_validator

logger = logging.getLogger("app.config")

INSECURE_DEV_SECRET = "dev-insecure-secret-key-only-for-local-testing-min-32-chars"
LEGACY_DEFAULT_SECRET = "production-ready-jwt-secret-key-replace-in-env-at-least-32-chars-long"


class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Resume Analyzer & Job Matcher"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"  # "development", "testing", "production"
    
    # Security
    SECRET_KEY: str = INSECURE_DEV_SECRET
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_AUTH_PER_MINUTE: int = 10
    RATE_LIMIT_UPLOAD_PER_MINUTE: int = 15
    RATE_LIMIT_ANALYSIS_PER_MINUTE: int = 20
    
    # Database
    DATABASE_URL: str = "sqlite:///./resume_matcher.db"
    AUTO_RUN_MIGRATIONS: bool = False
    
    # CORS
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]
    
    # Upload limits
    MAX_FILE_SIZE_BYTES: int = 5 * 1024 * 1024  # 5 MB
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".docx"]
    
    # Optional LLM integration
    LLM_PROVIDER: str = "none"  # "none", "gemini", "openai"
    LLM_API_KEY: Union[str, None] = None
    LLM_MODEL: Union[str, None] = None

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            origins = [i.strip() for i in v.split(",") if i.strip()]
            return origins
        elif isinstance(v, list):
            return [str(i).strip() for i in v if str(i).strip()]
        return ["http://localhost:5173", "http://127.0.0.1:5173"]

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        is_production = self.ENVIRONMENT.lower() == "production"
        
        # Enforce strong secret in production
        if is_production:
            if (
                not self.SECRET_KEY
                or self.SECRET_KEY in [INSECURE_DEV_SECRET, LEGACY_DEFAULT_SECRET, "secret", "changeme", "password"]
                or len(self.SECRET_KEY) < 32
            ):
                raise ValueError(
                    "CRITICAL SECURITY CONFIGURATION: In production (ENVIRONMENT=production), "
                    "SECRET_KEY must be set via environment variable to a strong, unique secret "
                    "at least 32 characters long. Generate one using: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
                )
            
            # Disallow wildcard in CORS when credentials are allowed
            if "*" in self.CORS_ORIGINS:
                raise ValueError(
                    "In production, CORS_ORIGINS must not contain wildcard '*' because credentialed requests are allowed."
                )
        else:
            if self.SECRET_KEY in [INSECURE_DEV_SECRET, LEGACY_DEFAULT_SECRET]:
                logger.warning(
                    "[SECURITY WARNING] Using default development SECRET_KEY. Set a strong SECRET_KEY in your .env file."
                )
        
        return self

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
