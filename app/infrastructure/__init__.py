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
    SQLiteAuditLogRepository,
    SQLiteInteractionRepository,
    SQLiteJamRepository,
    SQLitePlanRepository,
    SQLitePlaylistRepository,
    SQLiteReviewRepository,
    SQLiteTrackRepository,
    SQLiteUserRepository,
)
from app.infrastructure.security import PBKDF2PasswordHasher
from app.infrastructure.telemetry import (
    CorrelationIdMiddleware,
    JSONLogFormatter,
    configure_logging,
    log_operational_event,
)

__all__ = [
    "CorrelationIdMiddleware",
    "DEFAULT_DATABASE_PATH",
    "ITunesAdapter",
    "JSONLogFormatter",
    "PBKDF2PasswordHasher",
    "SQLiteAuditLogRepository",
    "SQLiteInteractionRepository",
    "SQLiteJamRepository",
    "SQLitePlanRepository",
    "SQLitePlaylistRepository",
    "SQLiteReviewRepository",
    "SQLiteTrackRepository",
    "SQLiteUserRepository",
    "SpotifyAdapter",
    "configure_logging",
    "create_connection",
    "log_operational_event",
    "transaction",
]
