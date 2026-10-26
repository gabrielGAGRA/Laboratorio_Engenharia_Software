"""Infrastructure adapters package exporting concrete implementations."""

from app.infrastructure.adapters.itunes.itunes_adapter import ITunesAdapter
from app.infrastructure.adapters.music_service import ExternalMusicServiceAdapter
from app.infrastructure.adapters.security.password_hasher import (
    PBKDF2PasswordHasher,
)
from app.infrastructure.adapters.spotify.spotify_adapter import SpotifyAdapter
from app.infrastructure.adapters.sqlite.connection import (
    DEFAULT_DATABASE_PATH,
    create_connection,
    transaction,
)
from app.infrastructure.adapters.sqlite.repositories.interaction_repository import (
    SQLiteInteractionRepository,
)
from app.infrastructure.adapters.sqlite.repositories.jam_repository import (
    SQLiteJamRepository,
)
from app.infrastructure.adapters.sqlite.repositories.plan_repository import (
    SQLitePlanRepository,
)
from app.infrastructure.adapters.sqlite.repositories.playlist_repository import (
    SQLitePlaylistRepository,
)
from app.infrastructure.adapters.sqlite.repositories.review_repository import (
    SQLiteReviewRepository,
)
from app.infrastructure.adapters.sqlite.repositories.track_repository import (
    SQLiteTrackRepository,
)
from app.infrastructure.adapters.sqlite.repositories.user_repository import (
    SQLiteUserRepository,
)
from app.infrastructure.adapters.sqlite.setup import init_db

__all__ = [
    "DEFAULT_DATABASE_PATH",
    "ExternalMusicServiceAdapter",
    "ITunesAdapter",
    "PBKDF2PasswordHasher",
    "SQLiteInteractionRepository",
    "SQLiteJamRepository",
    "SQLitePlanRepository",
    "SQLitePlaylistRepository",
    "SQLiteReviewRepository",
    "SQLiteTrackRepository",
    "SQLiteUserRepository",
    "SpotifyAdapter",
    "create_connection",
    "init_db",
    "transaction",
]
