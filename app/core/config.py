from functools import lru_cache

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    project_name: str = "Culture Document Flow API"
    app_env: str = "local"
    debug: bool = Field(default=True, validation_alias="APP_DEBUG")
    api_v1_prefix: str = "/api"

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "culture_docs"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"

    upload_dir: str = "uploads"

    jwt_secret_key: str = Field(default="change-me", min_length=8)
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30

    @computed_field
    @property
    def database_url(self) -> str:
        return (
            "postgresql+asyncpg://"
            f"{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
