from pathlib import Path

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

CONFIG_DIR = Path(__file__).parent
PROJECT_NAME: str = 'HarmonIA Alpha'


class Settings(BaseSettings):
    # Banco Relacional (Backend)
    DB_HOST: str = Field(default='localhost', env='DB_HOST')
    DB_PORT: int = Field(..., env='DB_PORT')
    DB_USER: str = Field(..., env='DB_USER')
    DB_PASS: str = Field(..., env='DB_PASS')
    DB_NAME: str = Field(..., env='DB_NAME')

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

    DATABASE_URL_SQLITE: str = 'sqlite:///database.db'

    model_config = SettingsConfigDict(
        env_file=str(CONFIG_DIR / '.env'),
        env_file_encoding='utf-8',
        extra='ignore',
        case_sensitive=True,
    )


settings = Settings()
