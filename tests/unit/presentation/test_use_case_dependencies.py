"""Unit tests for presentation use case dependency providers."""

from typing import Any
from unittest.mock import MagicMock
lazy from collections.abc import Callable

import pytest
from fastapi import Request

from app.presentation.dependencies import use_cases


@pytest.mark.parametrize(
    ("provider_fn", "container_attr"),
    [
        (use_cases.get_register_user_use_case, "register_user_use_case"),
        (use_cases.get_authenticate_user_use_case, "authenticate_user_use_case"),
        (use_cases.get_authenticate_admin_use_case, "authenticate_admin_use_case"),
        (
            use_cases.get_next_discovery_track_use_case,
            "get_next_discovery_track_use_case",
        ),
        (
            use_cases.get_record_swipe_interaction_use_case,
            "record_swipe_interaction_use_case",
        ),
        (use_cases.get_create_deck_playlist_use_case, "create_deck_playlist_use_case"),
        (
            use_cases.get_add_track_to_playlist_use_case,
            "add_track_to_playlist_use_case",
        ),
        (use_cases.get_list_user_playlists_use_case, "list_user_playlists_use_case"),
        (
            use_cases.get_export_playlist_to_spotify_use_case,
            "export_playlist_to_spotify_use_case",
        ),
        (use_cases.get_create_jam_use_case, "create_jam_use_case"),
        (use_cases.get_join_jam_use_case, "join_jam_use_case"),
        (use_cases.get_jam_state_use_case, "get_jam_state_use_case"),
        (use_cases.get_vote_jam_track_use_case, "vote_jam_track_use_case"),
        (use_cases.get_vote_skip_jam_track_use_case, "vote_skip_jam_track_use_case"),
        (
            use_cases.get_advance_jam_playback_use_case,
            "advance_jam_playback_use_case",
        ),
        (use_cases.get_search_tracks_use_case, "search_tracks_use_case"),
        (use_cases.get_publish_review_use_case, "publish_review_use_case"),
        (use_cases.get_community_feed_use_case, "get_community_feed_use_case"),
        (use_cases.get_like_review_comment_use_case, "like_review_comment_use_case"),
        (use_cases.get_track_reviews_use_case, "get_track_reviews_use_case"),
        (use_cases.get_user_profile_use_case, "get_user_profile_use_case"),
        (use_cases.get_update_profile_use_case, "update_profile_use_case"),
        (use_cases.get_delete_user_account_use_case, "delete_user_account_use_case"),
        (use_cases.get_list_plans_use_case, "list_plans_use_case"),
        (
            use_cases.get_change_subscription_plan_use_case,
            "change_subscription_plan_use_case",
        ),
        (
            use_cases.get_cancel_subscription_plan_use_case,
            "cancel_subscription_plan_use_case",
        ),
        (use_cases.get_add_family_member_use_case, "add_family_member_use_case"),
        (use_cases.get_remove_family_member_use_case, "remove_family_member_use_case"),
        (use_cases.get_list_family_members_use_case, "list_family_members_use_case"),
        (use_cases.get_list_blocked_genres_use_case, "list_blocked_genres_use_case"),
        (
            use_cases.get_update_blocked_genres_use_case,
            "update_blocked_genres_use_case",
        ),
        (
            use_cases.get_list_user_interactions_use_case,
            "list_user_interactions_use_case",
        ),
        (
            use_cases.get_change_track_interaction_use_case,
            "change_track_interaction_use_case",
        ),
        (
            use_cases.get_annual_stats_use_case,
            "get_annual_listening_stats_use_case",
        ),
        (
            use_cases.get_annual_listening_stats_use_case,
            "get_annual_listening_stats_use_case",
        ),
        (
            use_cases.get_link_spotify_account_use_case,
            "link_spotify_account_use_case",
        ),
        (
            use_cases.get_executive_dashboard_use_case,
            "get_executive_dashboard_use_case",
        ),
        (
            use_cases.get_list_users_with_plans_use_case,
            "list_users_with_plans_use_case",
        ),
        (use_cases.get_audience_report_use_case, "get_audience_report_use_case"),
        (use_cases.get_block_track_use_case, "block_track_use_case"),
        (
            use_cases.get_update_track_explicit_flag_use_case,
            "update_track_explicit_flag_use_case",
        ),
        (
            use_cases.get_promote_user_to_admin_use_case,
            "promote_user_to_admin_use_case",
        ),
        (
            use_cases.get_update_subscription_plan_use_case,
            "update_subscription_plan_use_case",
        ),
        (
            use_cases.get_top_moderation_reviews_use_case,
            "get_top_moderation_reviews_use_case",
        ),
        (use_cases.get_audit_logs_use_case, "get_audit_logs_use_case"),
    ],
)
def test_use_case_dependency_provider_resolves_from_request_container(
    provider_fn: Callable[[Request], Any],
    container_attr: str,
) -> None:
    request = MagicMock(spec=Request)
    container = MagicMock()
    expected = sentinel("USE_CASE")
    setattr(container, container_attr, expected)
    request.app.state.container = container

    resolved = provider_fn(request)

    assert resolved is expected
