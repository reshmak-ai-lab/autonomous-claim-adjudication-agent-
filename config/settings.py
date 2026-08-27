from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigdict


class Settings(BaseSettings):
    """
    Central application configuration.

    Values are loaded from:
    1. Environment variables
    2. .env file
    3. Defaults defined below
    """

    model_config = SettingsConfigdict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # =========================================================
    # Application
    # =========================================================

    APP_NAME: str = "Autonomous Claim Adjudication & Fraud Detection Agent"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # =========================================================
    # Database
    # =========================================================

    DATABASE_URL: str = "sqlite:///./claims.db"
    DATABASE_ECHO: bool = False

    # =========================================================
    # OpenAI / LLM
    # =========================================================

    OPENAI_API_KEY: str = Field(
        default="",
        repr=False,
    )

    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_TEMPERATURE: float = 0.0

    # =========================================================
    # LangChain
    # =========================================================

    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_API_KEY: str = Field(
        default="",
        repr=False,
    )

    LANGCHAIN_PROJECT: str = (
        "autonomous-claim-adjudication"
    )

    LANGCHAIN_ENDPOINT: str = (
        "https://api.smith.langchain.com"
    )

    # =========================================================
    # Vector Database / RAG
    # =========================================================

    VECTOR_DB: str = "faiss"

    VECTORSTORE_PATH: str = "./vectorstore"

    EMBEDDING_MODEL: str = (
        "text-embedding-3-small"
    )

    RAG_TOP_K: int = 5

    RAG_SCORE_THRESHOLD: float = 0.50

    # =========================================================
    # Policy Data
    # =========================================================

    POLICY_DATA_PATH: str = "./data/policies"

    CLAIM_DATA_PATH: str = "./data/sample_claims"

    MEDICAL_DOCUMENT_PATH: str = (
        "./data/medical_documents"
    )

    HOSPITAL_DATA_PATH: str = (
        "./data/hospital"
    )

    EVALUATION_DATA_PATH: str = (
        "./data/evaluation"
    )

    # =========================================================
    # Mem0
    # =========================================================

    MEM0_API_KEY: str = Field(
        default="",
        repr=False,
    )

    MEM0_ENABLED: bool = True

    # =========================================================
    # MCP Services
    # =========================================================

    MCP_ENABLED: bool = True

    MCP_POLICY_URL: str = (
        "http://localhost:8001"
    )

    MCP_ICD10_URL: str = (
        "http://localhost:8002"
    )

    MCP_TARIFF_URL: str = (
        "http://localhost:8003"
    )

    MCP_CALCULATION_URL: str = (
        "http://localhost:8004"
    )

    MCP_TIMEOUT_SECONDS: int = 10

    # =========================================================
    # Redis
    # =========================================================

    REDIS_ENABLED: bool = False

    REDIS_URL: str = (
        "redis://localhost:6379/0"
    )

    REDIS_CACHE_TTL: int = 3600

    # =========================================================
    # Presidio / Privacy
    # =========================================================

    PRESIDIO_ENABLED: bool = True

    PII_REDACTION_ENABLED: bool = True

    PII_REPLACEMENT_FORMAT: str = (
        "[REDACTED_{entity_type}]"
    )

    # =========================================================
    # Claim Processing
    # =========================================================

    DEFAULT_CURRENCY: str = "INR"

    DEFAULT_COUNTRY: str = "India"

    DEFAULT_PED_WAITING_MONTHS: int = 36

    DEFAULT_ROOM_RENT_PERCENTAGE: float = 1.0

    DEFAULT_COPAY_PERCENTAGE: float = 10.0

    # =========================================================
    # Fraud Detection
    # =========================================================

    FRAUD_DETECTION_ENABLED: bool = True

    FRAUD_LOW_THRESHOLD: float = 0.30

    FRAUD_MEDIUM_THRESHOLD: float = 0.60

    FRAUD_HIGH_THRESHOLD: float = 0.80

    # =========================================================
    # Agent / Decision
    # =========================================================

    CONFIDENCE_THRESHOLD: float = 0.75

    HUMAN_REVIEW_THRESHOLD: float = 0.60

    MAX_AGENT_RETRIES: int = 2

    # =========================================================
    # Guardrails
    # =========================================================

    GUARDRAILS_ENABLED: bool = True

    MAX_QUERY_LENGTH: int = 5000

    MAX_DOCUMENT_SIZE_MB: int = 20

    BLOCK_PROMPT_INJECTION: bool = True

    VALIDATE_FINANCIAL_OUTPUT: bool = True

    VALIDATE_POLICY_DECISION: bool = True

    # =========================================================
    # Logging
    # =========================================================

    LOG_LEVEL: str = "INFO"

    LOG_FILE: str = "logs/application.log"

    # =========================================================
    # Security
    # =========================================================

    SECRET_KEY: str = Field(
        default="change-this-in-production",
        repr=False,
    )

    # =========================================================
    # CORS
    # =========================================================

    CORS_ORIGINS: str = "http://localhost:8501"

    @property
    def cors_origins_list(self) -> List[str]:
        """
        Convert comma-separated CORS origins into a list.
        """

        return [
            origin.strip()
            for origin in self.CORS_ORIGINS.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    """
    Return cached application settings.
    """

    return Settings()


settings = get_settings()