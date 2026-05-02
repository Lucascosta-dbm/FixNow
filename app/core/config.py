"""
Configurações centrais da aplicação FixNow.
Carrega variáveis de ambiente do arquivo .env.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")
    # Aplicação
    APP_NAME: str = "FixNow"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_SECRET_KEY: str = "chave-secreta-troque-em-producao"

    # API
    API_PREFIX: str = "/api/v1"

    # Banco de dados
    DATABASE_URL: str = "postgresql+asyncpg://fixnow:fixnow123@localhost:5432/fixnow_db"

    # JWT
    JWT_SECRET_KEY: str = "jwt-chave-secreta"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Pesos do algoritmo de matching
    MATCHING_WEIGHT_PROXIMITY: float = 0.30
    MATCHING_WEIGHT_RATING: float = 0.25
    MATCHING_WEIGHT_TRUST_SCORE: float = 0.20
    MATCHING_WEIGHT_AVAILABILITY: float = 0.15
    MATCHING_WEIGHT_RESPONSE_TIME: float = 0.10
    MATCHING_MAX_DISTANCE_KM: float = 30.0


# Instância global de configurações
settings = Settings()
