"""Application Data Transfer Objects (DTOs) for inputs and outputs."""

from app.application.dtos.admin_dtos import (
    AudienceReportResponse,
    AuditLogEntryResponse,
    ExecutiveDashboardResponse,
    UpdateSubscriptionPlanInput,
    UserPlanSummaryResponse,
)
from app.application.dtos.auth_dtos import (
    AuthenticateUserInput,
    RegisterUserInput,
)
from app.application.dtos.discovery_dtos import (
    InteractionResponse,
    RecordSwipeInput,
)
from app.application.dtos.jam_dtos import (
    CreateJamInput,
    JamQueueItemResponse,
    JamResponse,
    JamStateResponse,
    VoteJamTrackInput,
    VoteSkipJamTrackInput,
)
from app.application.dtos.plan_dtos import PlanResponse
from app.application.dtos.playlist_dtos import (
    AddTrackToPlaylistInput,
    CreateDeckPlaylistInput,
    PlaylistResponse,
)
from app.application.dtos.review_dtos import (
    PublishReviewInput,
    ReviewResponse,
    SearchTracksInput,
)
from app.application.dtos.track_dtos import TrackResponse
from app.application.dtos.user_dtos import (
    AnnualStatsResponse,
    UpdateProfileInput,
    UserProfileResponse,
    UserResponse,
)

__all__ = [
    "AddTrackToPlaylistInput",
    "AnnualStatsResponse",
    "AudienceReportResponse",
    "AuditLogEntryResponse",
    "AuthenticateUserInput",
    "CreateDeckPlaylistInput",
    "CreateJamInput",
    "ExecutiveDashboardResponse",
    "InteractionResponse",
    "JamQueueItemResponse",
    "JamResponse",
    "JamStateResponse",
    "PlanResponse",
    "PlaylistResponse",
    "PublishReviewInput",
    "RecordSwipeInput",
    "RegisterUserInput",
    "ReviewResponse",
    "SearchTracksInput",
    "TrackResponse",
    "UpdateProfileInput",
    "UpdateSubscriptionPlanInput",
    "UserProfileResponse",
    "UserPlanSummaryResponse",
    "UserResponse",
    "VoteJamTrackInput",
    "VoteSkipJamTrackInput",
]
