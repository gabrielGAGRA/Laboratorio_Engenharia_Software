"""Inbound application commands."""

from app.application.commands.admin_commands import (
    UpdateSubscriptionPlanCommand,
)
from app.application.commands.auth_commands import (
    AuthenticateAdminCommand,
    AuthenticateUserCommand,
    RegisterUserCommand,
)
from app.application.commands.discovery_commands import RecordSwipeCommand
from app.application.commands.jam_commands import (
    CreateJamCommand,
    VoteJamTrackCommand,
    VoteSkipJamTrackCommand,
)
from app.application.commands.playlist_commands import (
    AddTrackToPlaylistCommand,
    CreateDeckPlaylistCommand,
)
from app.application.commands.review_commands import (
    PublishReviewCommand,
    SearchTracksCommand,
)
from app.application.commands.user_commands import UpdateProfileCommand

__all__ = [
    "AddTrackToPlaylistCommand",
    "AuthenticateAdminCommand",
    "AuthenticateUserCommand",
    "CreateDeckPlaylistCommand",
    "CreateJamCommand",
    "PublishReviewCommand",
    "RecordSwipeCommand",
    "RegisterUserCommand",
    "SearchTracksCommand",
    "UpdateProfileCommand",
    "UpdateSubscriptionPlanCommand",
    "VoteJamTrackCommand",
    "VoteSkipJamTrackCommand",
]
