# config/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, AliasChoices
from pathlib import Path

CONFIG_DIR = Path(__file__).parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "HarmonIA Alpha"
    DEBUG: bool = True 

    # --- Weaviate ---
    WEAVIATE_HOST: str = Field(default="localhost", validation_alias="WEAVIATE_HOST")
    WEAVIATE_HTTP_PORT: int = Field(default=8080, validation_alias="WEAVIATE_HTTP_PORT")
    WEAVIATE_GRPC_PORT: int = Field(default=50051, validation_alias="WEAVIATE_GRPC_PORT")
    COLLECTION_NAME: str = Field(default="harmonia_tool", validation_alias="COLLECTION_NAME")

    # --- Modelos ---
    EMBEDDING_MODEL_ID: str = Field(default="modelos/LaBSE_int8", validation_alias="EMBEDDING_MODEL_ID")

    #--- Performance ---
    USE_GPU: bool = Field(default=False, validation_alias="USE_GPU")
    THREADS: int = Field(default=8, validation_alias="THREADS")
    CHUNK_SIZE: int = Field(default=200, validation_alias="CHUNK_SIZE")
    CHUNK_OVERLAP: int = Field(default=30, validation_alias="CHUNK_OVERLAP")

    model_config = SettingsConfigDict(
        env_file=str(CONFIG_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
