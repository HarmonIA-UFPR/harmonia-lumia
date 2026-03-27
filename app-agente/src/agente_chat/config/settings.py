# config/settings.py

"""
Configurações centralizadas do Agente Chat.
Agora com suporte a PostgreSQL para persistência do histórico de chat.
"""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

CONFIG_DIR = Path(__file__).parent


class Settings(BaseSettings):
    """Configurações carregadas do .env."""

    PROJECT_NAME: str = "HarmonIA Agente Chat"
    DEBUG: bool = True

    # --- PostgreSQL ---
    AGENTE_HOST: str = Field(..., validation_alias="AGENTE_HOST")
    AGENTE_PORT: int = Field(..., validation_alias="AGENTE_PORT")
    AGENTE_DB: str = Field(..., validation_alias="AGENTE_DB")
    AGENTE_USER: str = Field(..., validation_alias="AGENTE_USER")
    AGENTE_PASSWORD: str = Field(..., validation_alias="AGENTE_PASSWORD")
    AGENTE_SCHEMA: str = Field(..., validation_alias="AGENTE_SCHEMA")

    @property
    def postgres_dsn(self) -> str:
        """Retorna a connection string do PostgreSQL."""
        return (
            f"postgresql://{self.AGENTE_USER}:{self.AGENTE_PASSWORD}"
            f"@{self.AGENTE_HOST}:{self.AGENTE_PORT}/{self.AGENTE_DB}"
        )

    @property
    def async_postgres_dsn(self) -> str:
        """Retorna a async connection string do PostgreSQL."""
        return (
            f"postgresql://{self.AGENTE_USER}:{self.AGENTE_PASSWORD}"
            f"@{self.AGENTE_HOST}:{self.AGENTE_PORT}/{self.AGENTE_DB}"
        ).replace("postgresql://", "postgresql+asyncpg://")

    # --- Weaviate ---
    WEAVIATE_HOST: str = Field(..., validation_alias="WEAVIATE_HOST")
    WEAVIATE_HTTP_PORT: int = Field(..., validation_alias="WEAVIATE_HTTP_PORT")
    WEAVIATE_GRPC_PORT: int = Field(..., validation_alias="WEAVIATE_GRPC_PORT")
    COLLECTION_NAME: str = Field(..., validation_alias="COLLECTION_NAME")

    # --- Modelos ---
    LLM_MODEL_ID: str = Field(..., validation_alias="LLM_MODEL_ID")
    EMBEDDING_MODEL_ID: str = Field(..., validation_alias="EMBEDDING_MODEL_ID")

    # --- Performance ---
    USE_GPU: bool = Field(..., validation_alias="USE_GPU")
    THREADS: int = Field(..., validation_alias="THREADS")
    CHUNK_SIZE: int = Field(..., validation_alias="CHUNK_SIZE")
    CHUNK_OVERLAP: int = Field(..., validation_alias="CHUNK_OVERLAP")

    model_config = SettingsConfigDict(
        env_file=CONFIG_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
