"""Configuration settings for the Ribbit application."""

import os

from pydantic import BaseModel, ConfigDict


class Settings(BaseModel):
    """Configuration settings data model containing fields only."""

    model_config = ConfigDict(frozen=True, extra="ignore")

    database_path: str = "local.db"
    password_hash_iterations: int = 600_000
    spotify_token: str | None = None
    app_title: str = "Ribbit Platform API"
    app_description: str = (
        "Backend V0 with Hexagonal Architecture for Track Discovery and"
        " Collaborative Jams"
    )
    app_version: str = "0.1.0"
    environment: str = "development"
    log_level: str = "INFO"


def load_settings() -> Settings:
    """Loads configuration settings from environment variables with ergonomic defaults."""
    raw_iterations = os.getenv("PASSWORD_HASH_ITERATIONS")
    iterations = (
        int(raw_iterations) if raw_iterations and raw_iterations.isdigit() else 600_000
    )

    db_path = os.getenv("DATABASE_PATH") or os.getenv("DATABASE_URL") or "local.db"
    if db_path.startswith("sqlite:///"):
        db_path = db_path.removeprefix("sqlite:///")

    return Settings(
        database_path=db_path,
        password_hash_iterations=iterations,
        spotify_token=os.getenv("SPOTIFY_TOKEN"),
        app_title=os.getenv("APP_TITLE", "Ribbit Platform API"),
        app_description=os.getenv(
            "APP_DESCRIPTION",
            "Backend V0 with Hexagonal Architecture for Track Discovery and"
            " Collaborative Jams",
        ),
        app_version=os.getenv("APP_VERSION", "0.1.0"),
        environment=os.getenv("ENVIRONMENT", "development"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )


__all__ = ["Settings", "load_settings"]
