"""Routers package for presentation layer endpoints."""

from app.presentation.routers.admin import router as admin_router
from app.presentation.routers.auth import router as auth_router
from app.presentation.routers.discovery import router as discovery_router
from app.presentation.routers.jams import router as jams_router
from app.presentation.routers.playlists import router as playlists_router
from app.presentation.routers.profile import router as profile_router
from app.presentation.routers.tracks_reviews import router as tracks_reviews_router

__all__ = [
    "admin_router",
    "auth_router",
    "discovery_router",
    "jams_router",
    "playlists_router",
    "profile_router",
    "tracks_reviews_router",
]
