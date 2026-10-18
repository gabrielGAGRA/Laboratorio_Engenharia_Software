"""Concrete repository implementations conforming to application repository ports."""

from app.infrastructure.repositories.interaction_repository import (
    SQLiteInteractionRepository,
)
from app.infrastructure.repositories.jam_repository import (
    SQLiteJamRepository,
)
from app.infrastructure.repositories.plan_repository import (
    SQLitePlanRepository,
)
from app.infrastructure.repositories.playlist_repository import (
    SQLitePlaylistRepository,
)
from app.infrastructure.repositories.review_repository import (
    SQLiteReviewRepository,
)
from app.infrastructure.repositories.track_repository import (
    SQLiteTrackRepository,
)
from app.infrastructure.repositories.user_repository import (
    SQLiteUserRepository,
)

InteractionRepository = SQLiteInteractionRepository
JamRepository = SQLiteJamRepository
PlanRepository = SQLitePlanRepository
PlaylistRepository = SQLitePlaylistRepository
ReviewRepository = SQLiteReviewRepository
TrackRepository = SQLiteTrackRepository
UserRepository = SQLiteUserRepository

__all__ = [
    "InteractionRepository",
    "JamRepository",
    "PlanRepository",
    "PlaylistRepository",
    "ReviewRepository",
    "SQLiteInteractionRepository",
    "SQLiteJamRepository",
    "SQLitePlanRepository",
    "SQLitePlaylistRepository",
    "SQLiteReviewRepository",
    "SQLiteTrackRepository",
    "SQLiteUserRepository",
    "TrackRepository",
    "UserRepository",
]
