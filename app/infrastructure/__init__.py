"""Infrastructure layer package providing external I/O adapters and persistence."""

from app.infrastructure.adapters import (
    ITunesAdapter,
    SpotifyAdapter,
)
from app.infrastructure.persistence import (
    DEFAULT_DATABASE_PATH,
    create_connection,
    transaction,
)
from app.infrastructure.repositories import (
    SQLiteInteractionRepository,
    SQLiteJamRepository,
    SQLitePlanRepository,
    SQLitePlaylistRepository,
    SQLiteReviewRepository,
    SQLiteTrackRepository,
    SQLiteUserRepository,
)
from app.infrastructure.security import PBKDF2PasswordHasher

__all__ = [
    "DEFAULT_DATABASE_PATH",
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
    "transaction",
]
