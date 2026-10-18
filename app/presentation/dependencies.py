"""Dependency injection providers for application use cases and presentation auth."""

from typing import TYPE_CHECKING, Annotated

from fastapi import Depends, Header

from app.domain.exceptions import AuthenticationRequiredError

if TYPE_CHECKING:
    from app.application.use_cases.admin import (
        BlockTrackUseCase,
        GetAudienceReportUseCase,
        GetAuditLogsUseCase,
        GetExecutiveDashboardUseCase,
        GetTopModerationReviewsUseCase,
        ListUsersWithPlansUseCase,
        PromoteUserToAdminUseCase,
        UpdateSubscriptionPlanUseCase,
        UpdateTrackExplicitFlagUseCase,
    )
    from app.application.use_cases.auth import (
        AuthenticateAdminUseCase,
        AuthenticateUserUseCase,
        RegisterUserUseCase,
    )
    from app.application.use_cases.discovery import (
        GetNextDiscoveryTrackUseCase,
        RecordSwipeInteractionUseCase,
    )
    from app.application.use_cases.jam import (
        AdvanceJamPlaybackUseCase,
        CreateJamUseCase,
        GetJamStateUseCase,
        JoinJamUseCase,
        VoteJamTrackUseCase,
        VoteSkipJamTrackUseCase,
    )
    from app.application.use_cases.playlist import (
        AddTrackToPlaylistUseCase,
        CreateDeckPlaylistUseCase,
        ExportPlaylistToSpotifyUseCase,
        ListUserPlaylistsUseCase,
    )
    from app.application.use_cases.review import (
        GetCommunityFeedUseCase,
        GetTrackReviewsUseCase,
        LikeReviewCommentUseCase,
        PublishReviewUseCase,
        SearchTracksUseCase,
    )
    from app.application.use_cases.user import (
        AddFamilyMemberUseCase,
        CancelSubscriptionPlanUseCase,
        ChangeSubscriptionPlanUseCase,
        ChangeTrackInteractionUseCase,
        DeleteUserAccountUseCase,
        GetAnnualListeningStatsUseCase,
        GetUserProfileUseCase,
        LinkSpotifyAccountUseCase,
        ListBlockedGenresUseCase,
        ListFamilyMembersUseCase,
        ListPlansUseCase,
        ListUserInteractionsUseCase,
        RemoveFamilyMemberUseCase,
        UpdateBlockedGenresUseCase,
        UpdateProfileUseCase,
    )

ADMIN_ID_HEADER = "X-Admin-Id"


def get_admin_id(
    admin_id: Annotated[int | None, Header(alias=ADMIN_ID_HEADER)] = None,
) -> int:
    """Extracts and validates that an administrator ID header is present."""
    if admin_id is None:
        raise AuthenticationRequiredError("Administrator ID header missing.")
    return admin_id


def require_admin(admin_id: Annotated[int, Depends(get_admin_id)]) -> int:
    """Enforces admin credential existence. Overridden by composition root for DB check."""
    return admin_id


# --- Auth Use Cases ---


def get_authenticate_admin_use_case() -> AuthenticateAdminUseCase:
    raise NotImplementedError(
        "AuthenticateAdminUseCase must be wired by composition root."
    )


def get_authenticate_user_use_case() -> AuthenticateUserUseCase:
    raise NotImplementedError(
        "AuthenticateUserUseCase must be wired by composition root."
    )


def get_register_user_use_case() -> RegisterUserUseCase:
    raise NotImplementedError("RegisterUserUseCase must be wired by composition root.")


# --- Discovery Use Cases ---


def get_next_discovery_track_use_case() -> GetNextDiscoveryTrackUseCase:
    raise NotImplementedError(
        "GetNextDiscoveryTrackUseCase must be wired by composition root."
    )


def get_record_swipe_interaction_use_case() -> RecordSwipeInteractionUseCase:
    raise NotImplementedError(
        "RecordSwipeInteractionUseCase must be wired by composition root."
    )


# --- Playlist Use Cases ---


def get_create_deck_playlist_use_case() -> CreateDeckPlaylistUseCase:
    raise NotImplementedError(
        "CreateDeckPlaylistUseCase must be wired by composition root."
    )


def get_add_track_to_playlist_use_case() -> AddTrackToPlaylistUseCase:
    raise NotImplementedError(
        "AddTrackToPlaylistUseCase must be wired by composition root."
    )


def get_list_user_playlists_use_case() -> ListUserPlaylistsUseCase:
    raise NotImplementedError(
        "ListUserPlaylistsUseCase must be wired by composition root."
    )


def get_export_playlist_to_spotify_use_case() -> ExportPlaylistToSpotifyUseCase:
    raise NotImplementedError(
        "ExportPlaylistToSpotifyUseCase must be wired by composition root."
    )


# --- Jam Use Cases ---


def get_create_jam_use_case() -> CreateJamUseCase:
    raise NotImplementedError("CreateJamUseCase must be wired by composition root.")


def get_join_jam_use_case() -> JoinJamUseCase:
    raise NotImplementedError("JoinJamUseCase must be wired by composition root.")


def get_jam_state_use_case() -> GetJamStateUseCase:
    raise NotImplementedError("GetJamStateUseCase must be wired by composition root.")


def get_vote_jam_track_use_case() -> VoteJamTrackUseCase:
    raise NotImplementedError("VoteJamTrackUseCase must be wired by composition root.")


def get_vote_skip_jam_track_use_case() -> VoteSkipJamTrackUseCase:
    raise NotImplementedError(
        "VoteSkipJamTrackUseCase must be wired by composition root."
    )


def get_advance_jam_playback_use_case() -> AdvanceJamPlaybackUseCase:
    raise NotImplementedError(
        "AdvanceJamPlaybackUseCase must be wired by composition root."
    )


# --- Review & Track Catalog Use Cases ---


def get_search_tracks_use_case() -> SearchTracksUseCase:
    raise NotImplementedError("SearchTracksUseCase must be wired by composition root.")


def get_publish_review_use_case() -> PublishReviewUseCase:
    raise NotImplementedError("PublishReviewUseCase must be wired by composition root.")


def get_community_feed_use_case() -> GetCommunityFeedUseCase:
    raise NotImplementedError(
        "GetCommunityFeedUseCase must be wired by composition root."
    )


def get_like_review_comment_use_case() -> LikeReviewCommentUseCase:
    raise NotImplementedError(
        "LikeReviewCommentUseCase must be wired by composition root."
    )


def get_track_reviews_use_case() -> GetTrackReviewsUseCase:
    raise NotImplementedError(
        "GetTrackReviewsUseCase must be wired by composition root."
    )


# --- Admin Use Cases ---


def get_executive_dashboard_use_case() -> GetExecutiveDashboardUseCase:
    raise NotImplementedError(
        "GetExecutiveDashboardUseCase must be wired by composition root."
    )


def get_list_users_with_plans_use_case() -> ListUsersWithPlansUseCase:
    raise NotImplementedError(
        "ListUsersWithPlansUseCase must be wired by composition root."
    )


def get_audience_report_use_case() -> GetAudienceReportUseCase:
    raise NotImplementedError(
        "GetAudienceReportUseCase must be wired by composition root."
    )


def get_block_track_use_case() -> BlockTrackUseCase:
    raise NotImplementedError("BlockTrackUseCase must be wired by composition root.")


def get_update_track_explicit_flag_use_case() -> UpdateTrackExplicitFlagUseCase:
    raise NotImplementedError(
        "UpdateTrackExplicitFlagUseCase must be wired by composition root."
    )


def get_promote_user_to_admin_use_case() -> PromoteUserToAdminUseCase:
    raise NotImplementedError(
        "PromoteUserToAdminUseCase must be wired by composition root."
    )


def get_update_subscription_plan_use_case() -> UpdateSubscriptionPlanUseCase:
    raise NotImplementedError(
        "UpdateSubscriptionPlanUseCase must be wired by composition root."
    )


def get_top_moderation_reviews_use_case() -> GetTopModerationReviewsUseCase:
    raise NotImplementedError(
        "GetTopModerationReviewsUseCase must be wired by composition root."
    )


def get_audit_logs_use_case() -> GetAuditLogsUseCase:
    raise NotImplementedError("GetAuditLogsUseCase must be wired by composition root.")


# --- User & Profile Use Cases ---


def get_user_profile_use_case() -> GetUserProfileUseCase:
    raise NotImplementedError(
        "GetUserProfileUseCase must be wired by composition root."
    )


def get_update_profile_use_case() -> UpdateProfileUseCase:
    raise NotImplementedError("UpdateProfileUseCase must be wired by composition root.")


def get_link_spotify_account_use_case() -> LinkSpotifyAccountUseCase:
    raise NotImplementedError(
        "LinkSpotifyAccountUseCase must be wired by composition root."
    )


def get_list_plans_use_case() -> ListPlansUseCase:
    raise NotImplementedError("ListPlansUseCase must be wired by composition root.")


def get_change_subscription_plan_use_case() -> ChangeSubscriptionPlanUseCase:
    raise NotImplementedError(
        "ChangeSubscriptionPlanUseCase must be wired by composition root."
    )


def get_cancel_subscription_plan_use_case() -> CancelSubscriptionPlanUseCase:
    raise NotImplementedError(
        "CancelSubscriptionPlanUseCase must be wired by composition root."
    )


def get_delete_user_account_use_case() -> DeleteUserAccountUseCase:
    raise NotImplementedError(
        "DeleteUserAccountUseCase must be wired by composition root."
    )


def get_annual_stats_use_case() -> GetAnnualListeningStatsUseCase:
    raise NotImplementedError(
        "GetAnnualListeningStatsUseCase must be wired by composition root."
    )


def get_change_track_interaction_use_case() -> ChangeTrackInteractionUseCase:
    raise NotImplementedError(
        "ChangeTrackInteractionUseCase must be wired by composition root."
    )


def get_list_user_interactions_use_case() -> ListUserInteractionsUseCase:
    raise NotImplementedError(
        "ListUserInteractionsUseCase must be wired by composition root."
    )


def get_list_blocked_genres_use_case() -> ListBlockedGenresUseCase:
    raise NotImplementedError(
        "ListBlockedGenresUseCase must be wired by composition root."
    )


def get_update_blocked_genres_use_case() -> UpdateBlockedGenresUseCase:
    raise NotImplementedError(
        "UpdateBlockedGenresUseCase must be wired by composition root."
    )


def get_list_family_members_use_case() -> ListFamilyMembersUseCase:
    raise NotImplementedError(
        "ListFamilyMembersUseCase must be wired by composition root."
    )


def get_add_family_member_use_case() -> AddFamilyMemberUseCase:
    raise NotImplementedError(
        "AddFamilyMemberUseCase must be wired by composition root."
    )


def get_remove_family_member_use_case() -> RemoveFamilyMemberUseCase:
    raise NotImplementedError(
        "RemoveFamilyMemberUseCase must be wired by composition root."
    )
