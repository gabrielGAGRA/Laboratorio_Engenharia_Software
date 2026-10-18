"""Dependency providers retrieving application use cases from container state."""

from typing import TYPE_CHECKING, cast

from fastapi import Request

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
    from app.composition import Container


def _container(request: Request) -> Container:
    return cast("Container", request.app.state.container)


# --- Auth ---
def get_register_user_use_case(request: Request) -> RegisterUserUseCase:
    return _container(request).register_user_use_case


def get_authenticate_user_use_case(request: Request) -> AuthenticateUserUseCase:
    return _container(request).authenticate_user_use_case


def get_authenticate_admin_use_case(request: Request) -> AuthenticateAdminUseCase:
    return _container(request).authenticate_admin_use_case


# --- Discovery ---
def get_next_discovery_track_use_case(
    request: Request,
) -> GetNextDiscoveryTrackUseCase:
    return _container(request).get_next_discovery_track_use_case


def get_record_swipe_interaction_use_case(
    request: Request,
) -> RecordSwipeInteractionUseCase:
    return _container(request).record_swipe_interaction_use_case


# --- Playlist ---
def get_create_deck_playlist_use_case(
    request: Request,
) -> CreateDeckPlaylistUseCase:
    return _container(request).create_deck_playlist_use_case


def get_add_track_to_playlist_use_case(
    request: Request,
) -> AddTrackToPlaylistUseCase:
    return _container(request).add_track_to_playlist_use_case


def get_list_user_playlists_use_case(
    request: Request,
) -> ListUserPlaylistsUseCase:
    return _container(request).list_user_playlists_use_case


def get_export_playlist_to_spotify_use_case(
    request: Request,
) -> ExportPlaylistToSpotifyUseCase:
    return _container(request).export_playlist_to_spotify_use_case


# --- Jam ---
def get_create_jam_use_case(request: Request) -> CreateJamUseCase:
    return _container(request).create_jam_use_case


def get_join_jam_use_case(request: Request) -> JoinJamUseCase:
    return _container(request).join_jam_use_case


def get_jam_state_use_case(request: Request) -> GetJamStateUseCase:
    return _container(request).get_jam_state_use_case


def get_vote_jam_track_use_case(request: Request) -> VoteJamTrackUseCase:
    return _container(request).vote_jam_track_use_case


def get_vote_skip_jam_track_use_case(request: Request) -> VoteSkipJamTrackUseCase:
    return _container(request).vote_skip_jam_track_use_case


def get_advance_jam_playback_use_case(
    request: Request,
) -> AdvanceJamPlaybackUseCase:
    return _container(request).advance_jam_playback_use_case


# --- Review ---
def get_search_tracks_use_case(request: Request) -> SearchTracksUseCase:
    return _container(request).search_tracks_use_case


def get_publish_review_use_case(request: Request) -> PublishReviewUseCase:
    return _container(request).publish_review_use_case


def get_community_feed_use_case(request: Request) -> GetCommunityFeedUseCase:
    return _container(request).get_community_feed_use_case


def get_like_review_comment_use_case(request: Request) -> LikeReviewCommentUseCase:
    return _container(request).like_review_comment_use_case


def get_track_reviews_use_case(request: Request) -> GetTrackReviewsUseCase:
    return _container(request).get_track_reviews_use_case


# --- User ---
def get_user_profile_use_case(request: Request) -> GetUserProfileUseCase:
    return _container(request).get_user_profile_use_case


def get_update_profile_use_case(request: Request) -> UpdateProfileUseCase:
    return _container(request).update_profile_use_case


def get_delete_user_account_use_case(
    request: Request,
) -> DeleteUserAccountUseCase:
    return _container(request).delete_user_account_use_case


def get_list_plans_use_case(request: Request) -> ListPlansUseCase:
    return _container(request).list_plans_use_case


def get_change_subscription_plan_use_case(
    request: Request,
) -> ChangeSubscriptionPlanUseCase:
    return _container(request).change_subscription_plan_use_case


def get_cancel_subscription_plan_use_case(
    request: Request,
) -> CancelSubscriptionPlanUseCase:
    return _container(request).cancel_subscription_plan_use_case


def get_add_family_member_use_case(
    request: Request,
) -> AddFamilyMemberUseCase:
    return _container(request).add_family_member_use_case


def get_remove_family_member_use_case(
    request: Request,
) -> RemoveFamilyMemberUseCase:
    return _container(request).remove_family_member_use_case


def get_list_family_members_use_case(
    request: Request,
) -> ListFamilyMembersUseCase:
    return _container(request).list_family_members_use_case


def get_list_blocked_genres_use_case(
    request: Request,
) -> ListBlockedGenresUseCase:
    return _container(request).list_blocked_genres_use_case


def get_update_blocked_genres_use_case(
    request: Request,
) -> UpdateBlockedGenresUseCase:
    return _container(request).update_blocked_genres_use_case


def get_list_user_interactions_use_case(
    request: Request,
) -> ListUserInteractionsUseCase:
    return _container(request).list_user_interactions_use_case


def get_change_track_interaction_use_case(
    request: Request,
) -> ChangeTrackInteractionUseCase:
    return _container(request).change_track_interaction_use_case


def get_annual_stats_use_case(
    request: Request,
) -> GetAnnualListeningStatsUseCase:
    return _container(request).get_annual_listening_stats_use_case


get_annual_listening_stats_use_case = get_annual_stats_use_case


def get_link_spotify_account_use_case(
    request: Request,
) -> LinkSpotifyAccountUseCase:
    return _container(request).link_spotify_account_use_case


# --- Admin ---
def get_executive_dashboard_use_case(
    request: Request,
) -> GetExecutiveDashboardUseCase:
    return _container(request).get_executive_dashboard_use_case


def get_list_users_with_plans_use_case(
    request: Request,
) -> ListUsersWithPlansUseCase:
    return _container(request).list_users_with_plans_use_case


def get_audience_report_use_case(
    request: Request,
) -> GetAudienceReportUseCase:
    return _container(request).get_audience_report_use_case


def get_block_track_use_case(request: Request) -> BlockTrackUseCase:
    return _container(request).block_track_use_case


def get_update_track_explicit_flag_use_case(
    request: Request,
) -> UpdateTrackExplicitFlagUseCase:
    return _container(request).update_track_explicit_flag_use_case


def get_promote_user_to_admin_use_case(
    request: Request,
) -> PromoteUserToAdminUseCase:
    return _container(request).promote_user_to_admin_use_case


def get_update_subscription_plan_use_case(
    request: Request,
) -> UpdateSubscriptionPlanUseCase:
    return _container(request).update_subscription_plan_use_case


def get_top_moderation_reviews_use_case(
    request: Request,
) -> GetTopModerationReviewsUseCase:
    return _container(request).get_top_moderation_reviews_use_case


def get_audit_logs_use_case(request: Request) -> GetAuditLogsUseCase:
    return _container(request).get_audit_logs_use_case


__all__ = [
    "get_add_family_member_use_case",
    "get_add_track_to_playlist_use_case",
    "get_advance_jam_playback_use_case",
    "get_annual_listening_stats_use_case",
    "get_annual_stats_use_case",
    "get_audience_report_use_case",
    "get_audit_logs_use_case",
    "get_authenticate_admin_use_case",
    "get_authenticate_user_use_case",
    "get_block_track_use_case",
    "get_cancel_subscription_plan_use_case",
    "get_change_subscription_plan_use_case",
    "get_change_track_interaction_use_case",
    "get_community_feed_use_case",
    "get_create_deck_playlist_use_case",
    "get_create_jam_use_case",
    "get_delete_user_account_use_case",
    "get_executive_dashboard_use_case",
    "get_export_playlist_to_spotify_use_case",
    "get_jam_state_use_case",
    "get_join_jam_use_case",
    "get_like_review_comment_use_case",
    "get_link_spotify_account_use_case",
    "get_list_blocked_genres_use_case",
    "get_list_family_members_use_case",
    "get_list_plans_use_case",
    "get_list_user_interactions_use_case",
    "get_list_user_playlists_use_case",
    "get_list_users_with_plans_use_case",
    "get_next_discovery_track_use_case",
    "get_promote_user_to_admin_use_case",
    "get_publish_review_use_case",
    "get_record_swipe_interaction_use_case",
    "get_register_user_use_case",
    "get_remove_family_member_use_case",
    "get_search_tracks_use_case",
    "get_top_moderation_reviews_use_case",
    "get_track_reviews_use_case",
    "get_update_blocked_genres_use_case",
    "get_update_profile_use_case",
    "get_update_subscription_plan_use_case",
    "get_update_track_explicit_flag_use_case",
    "get_user_profile_use_case",
    "get_vote_jam_track_use_case",
    "get_vote_skip_jam_track_use_case",
]
