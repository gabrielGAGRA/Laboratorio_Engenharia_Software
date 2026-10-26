"""Ribbit Platform Backend - Application Entrypoint."""

import logging

from app.composition import create_app
from app.config import load_settings

settings = load_settings()
logging.basicConfig(level=settings.log_level)

app = create_app(settings)

__all__ = ["app"]
