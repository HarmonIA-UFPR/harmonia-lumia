from pathlib import Path

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

CONFIG_DIR = Path(__file__).parent
BASE_DIR = Path(__file__).resolve().parent.parent.parent
PROJECT_NAME: str = 'HarmonIA Alpha'


class Settings(BaseSettings):
    # Banco Relacional (Backend)
    DB_HOST: str = Field(...)
    DB_PORT: int = Field(...)
    DB_USER: str = Field(...)
    DB_PASS: str = Field(...)
    DB_NAME: str = Field(...)

    # Security
    SECRET_KEY: str = Field(
        default='my-super-secret-key-change-it-later', env='SECRET_KEY'
    )
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Montagem dinâmica para PostgreSQL
    @computed_field
    @property
    def DATABASE_URL_PG(self) -> str:
        return (
            f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}'
            f'@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'
        )

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / '.env' if (BASE_DIR / '.env').exists() else None,
        env_file_encoding='utf-8',
        extra='ignore',
        case_sensitive=True,
    )


settings = Settings()
