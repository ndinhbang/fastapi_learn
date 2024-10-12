import os
import secrets
from typing import Annotated, Any, Literal

from pydantic import (
    AnyUrl,
    BeforeValidator,
    computed_field,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

env_file = os.path.join(os.path.dirname(__file__), "../.env")


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Use top level .env file (one level above ./backend/)
        env_file=env_file,
        env_ignore_empty=True,
        extra="ignore",
    )

    APP_NAME: str = "FastAPI"
    APP_KEY: str = secrets.token_urlsafe(32)
    APP_URL: str = "http://localhost:8000"
    APP_ENV: Literal["local", "staging", "production"] = "local"

    FRONTEND_URL: str = "http://localhost:5173"

    CORS_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = []

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.CORS_ORIGINS] + [
            self.APP_URL,
            self.FRONTEND_URL,
        ]

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str = ""
    DB_DATABASE: str

    SQLALCHEMY_ECHO: bool = False

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"mysql+asyncmy://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_DATABASE}"


settings = Settings()  # type: ignore
