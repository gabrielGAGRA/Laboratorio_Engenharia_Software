"""Composition root: inlines infrastructure, use case construction, and router mounting."""

import sqlite3
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any
lazy from collections.abc import AsyncGenerator

from fastapi import FastAPI

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
from app.config import Settings, load_settings
from app.infrastructure.adapters import SpotifyAdapter
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
from app.presentation.exception_handlers import register_exception_handlers
from app.presentation.routers.admin import router as admin_router
from app.presentation.routers.auth import router as auth_router
from app.presentation.routers.discovery import router as discovery_router
from app.presentation.routers.jams import router as jams_router
from app.presentation.routers.playlists import router as playlists_router
from app.presentation.routers.profile import router as profile_router
from app.presentation.routers.tracks_reviews import (
    router as tracks_reviews_router,
)


@dataclass(slots=True, kw_only=True)
class Container:
    """Dependency injection container holding application adapters and use cases."""

    settings: Settings
    connection: sqlite3.Connection
    password_hasher: PBKDF2PasswordHasher
    music_service: SpotifyAdapter
    user_repo: SQLiteUserRepository
    plan_repo: SQLitePlanRepository
    track_repo: SQLiteTrackRepository
    playlist_repo: SQLitePlaylistRepository
    interaction_repo: SQLiteInteractionRepository
    jam_repo: SQLiteJamRepository
    review_repo: SQLiteReviewRepository
    audit_log_repo: SQLiteAuditLogRepository
    # Auth
    register_user_use_case: RegisterUserUseCase
    authenticate_user_use_case: AuthenticateUserUseCase
    authenticate_admin_use_case: AuthenticateAdminUseCase
    # Discovery
    get_next_discovery_track_use_case: GetNextDiscoveryTrackUseCase
    record_swipe_interaction_use_case: RecordSwipeInteractionUseCase
    # Playlist
    create_deck_playlist_use_case: CreateDeckPlaylistUseCase
    add_track_to_playlist_use_case: AddTrackToPlaylistUseCase
    export_playlist_to_spotify_use_case: ExportPlaylistToSpotifyUseCase
    list_user_playlists_use_case: ListUserPlaylistsUseCase
    # Jam
    create_jam_use_case: CreateJamUseCase
    join_jam_use_case: JoinJamUseCase
    get_jam_state_use_case: GetJamStateUseCase
    vote_jam_track_use_case: VoteJamTrackUseCase
    vote_skip_jam_track_use_case: VoteSkipJamTrackUseCase
    advance_jam_playback_use_case: AdvanceJamPlaybackUseCase
    # Review
    search_tracks_use_case: SearchTracksUseCase
    publish_review_use_case: PublishReviewUseCase
    get_track_reviews_use_case: GetTrackReviewsUseCase
    get_community_feed_use_case: GetCommunityFeedUseCase
    like_review_comment_use_case: LikeReviewCommentUseCase
    # User
    get_user_profile_use_case: GetUserProfileUseCase
    update_profile_use_case: UpdateProfileUseCase
    delete_user_account_use_case: DeleteUserAccountUseCase
    list_plans_use_case: ListPlansUseCase
    change_subscription_plan_use_case: ChangeSubscriptionPlanUseCase
    cancel_subscription_plan_use_case: CancelSubscriptionPlanUseCase
    add_family_member_use_case: AddFamilyMemberUseCase
    remove_family_member_use_case: RemoveFamilyMemberUseCase
    list_family_members_use_case: ListFamilyMembersUseCase
    list_blocked_genres_use_case: ListBlockedGenresUseCase
    update_blocked_genres_use_case: UpdateBlockedGenresUseCase
    list_user_interactions_use_case: ListUserInteractionsUseCase
    change_track_interaction_use_case: ChangeTrackInteractionUseCase
    get_annual_listening_stats_use_case: GetAnnualListeningStatsUseCase
    link_spotify_account_use_case: LinkSpotifyAccountUseCase
    # Admin
    get_executive_dashboard_use_case: GetExecutiveDashboardUseCase
    list_users_with_plans_use_case: ListUsersWithPlansUseCase
    update_subscription_plan_use_case: UpdateSubscriptionPlanUseCase
    update_track_explicit_flag_use_case: UpdateTrackExplicitFlagUseCase
    block_track_use_case: BlockTrackUseCase
    get_top_moderation_reviews_use_case: GetTopModerationReviewsUseCase
    get_audience_report_use_case: GetAudienceReportUseCase
    get_audit_logs_use_case: GetAuditLogsUseCase
    promote_user_to_admin_use_case: PromoteUserToAdminUseCase

    def __getattr__(self, name: str) -> Any:
        use_case_name = f"{name}_use_case"
        try:
            return object.__getattribute__(self, use_case_name)
        except AttributeError:
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{name}'"
            ) from None


def build_container(
    settings: Settings,
    connection: sqlite3.Connection | None = None,
) -> Container:
    """Builds and wires all application infrastructure and use cases into a Container."""
    if connection is not None:
        conn = connection
    else:
        conn = sqlite3.connect(settings.database_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
    password_hasher = PBKDF2PasswordHasher(iterations=settings.password_hash_iterations)
    music_service = SpotifyAdapter(spotify_token=settings.spotify_token)

    user_repo = SQLiteUserRepository(conn)
    plan_repo = SQLitePlanRepository(conn)
    track_repo = SQLiteTrackRepository(conn)
    playlist_repo = SQLitePlaylistRepository(conn)
    interaction_repo = SQLiteInteractionRepository(conn)
    jam_repo = SQLiteJamRepository(conn)
    review_repo = SQLiteReviewRepository(conn)
    audit_log_repo = SQLiteAuditLogRepository(conn)

    return Container(
        settings=settings,
        connection=conn,
        password_hasher=password_hasher,
        music_service=music_service,
        user_repo=user_repo,
        plan_repo=plan_repo,
        track_repo=track_repo,
        playlist_repo=playlist_repo,
        interaction_repo=interaction_repo,
        jam_repo=jam_repo,
        review_repo=review_repo,
        audit_log_repo=audit_log_repo,
        # Auth
        register_user_use_case=RegisterUserUseCase(
            user_repo, plan_repo, password_hasher
        ),
        authenticate_user_use_case=AuthenticateUserUseCase(user_repo, password_hasher),
        authenticate_admin_use_case=AuthenticateAdminUseCase(
            user_repo, password_hasher
        ),
        # Discovery
        get_next_discovery_track_use_case=GetNextDiscoveryTrackUseCase(
            user_repo, track_repo, interaction_repo
        ),
        record_swipe_interaction_use_case=RecordSwipeInteractionUseCase(
            user_repo, track_repo, interaction_repo
        ),
        # Playlist
        create_deck_playlist_use_case=CreateDeckPlaylistUseCase(
            user_repo, track_repo, playlist_repo
        ),
        add_track_to_playlist_use_case=AddTrackToPlaylistUseCase(
            user_repo, track_repo, playlist_repo
        ),
        export_playlist_to_spotify_use_case=ExportPlaylistToSpotifyUseCase(
            user_repo, playlist_repo, music_service
        ),
        list_user_playlists_use_case=ListUserPlaylistsUseCase(user_repo, playlist_repo),
        # Jam
        create_jam_use_case=CreateJamUseCase(jam_repo, user_repo),
        join_jam_use_case=JoinJamUseCase(jam_repo),
        get_jam_state_use_case=GetJamStateUseCase(jam_repo, user_repo, track_repo),
        vote_jam_track_use_case=VoteJamTrackUseCase(jam_repo, user_repo, track_repo),
        vote_skip_jam_track_use_case=VoteSkipJamTrackUseCase(
            jam_repo, user_repo, track_repo
        ),
        advance_jam_playback_use_case=AdvanceJamPlaybackUseCase(jam_repo),
        # Review
        search_tracks_use_case=SearchTracksUseCase(user_repo, track_repo),
        publish_review_use_case=PublishReviewUseCase(
            user_repo, track_repo, review_repo
        ),
        get_track_reviews_use_case=GetTrackReviewsUseCase(track_repo, review_repo),
        get_community_feed_use_case=GetCommunityFeedUseCase(review_repo),
        like_review_comment_use_case=LikeReviewCommentUseCase(review_repo),
        # User
        get_user_profile_use_case=GetUserProfileUseCase(user_repo, plan_repo),
        update_profile_use_case=UpdateProfileUseCase(user_repo, password_hasher),
        delete_user_account_use_case=DeleteUserAccountUseCase(user_repo),
        list_plans_use_case=ListPlansUseCase(plan_repo),
        change_subscription_plan_use_case=ChangeSubscriptionPlanUseCase(
            user_repo, plan_repo
        ),
        cancel_subscription_plan_use_case=CancelSubscriptionPlanUseCase(
            user_repo, plan_repo
        ),
        add_family_member_use_case=AddFamilyMemberUseCase(user_repo, plan_repo),
        remove_family_member_use_case=RemoveFamilyMemberUseCase(user_repo, plan_repo),
        list_family_members_use_case=ListFamilyMembersUseCase(user_repo),
        list_blocked_genres_use_case=ListBlockedGenresUseCase(user_repo),
        update_blocked_genres_use_case=UpdateBlockedGenresUseCase(user_repo, plan_repo),
        list_user_interactions_use_case=ListUserInteractionsUseCase(
            user_repo, interaction_repo
        ),
        change_track_interaction_use_case=ChangeTrackInteractionUseCase(
            user_repo, plan_repo, interaction_repo
        ),
        get_annual_listening_stats_use_case=GetAnnualListeningStatsUseCase(
            user_repo, plan_repo, interaction_repo, track_repo
        ),
        link_spotify_account_use_case=LinkSpotifyAccountUseCase(user_repo),
        # Admin
        get_executive_dashboard_use_case=GetExecutiveDashboardUseCase(
            user_repo, plan_repo
        ),
        list_users_with_plans_use_case=ListUsersWithPlansUseCase(user_repo, plan_repo),
        update_subscription_plan_use_case=UpdateSubscriptionPlanUseCase(plan_repo),
        update_track_explicit_flag_use_case=UpdateTrackExplicitFlagUseCase(track_repo),
        block_track_use_case=BlockTrackUseCase(track_repo),
        get_top_moderation_reviews_use_case=GetTopModerationReviewsUseCase(review_repo),
        get_audience_report_use_case=GetAudienceReportUseCase(user_repo, track_repo),
        get_audit_logs_use_case=GetAuditLogsUseCase(audit_log_repo),
        promote_user_to_admin_use_case=PromoteUserToAdminUseCase(user_repo),
    )


def _mount_presentation_routers(app: FastAPI) -> None:
    """Mounts all presentation-layer routers individually."""
    for router in [
        auth_router,
        discovery_router,
        playlists_router,
        profile_router,
        jams_router,
        tracks_reviews_router,
        admin_router,
    ]:
        app.include_router(router)


def create_app(
    settings: Settings | None = None,
    connection: sqlite3.Connection | None = None,
) -> FastAPI:
    """Application factory building FastAPI app with Hexagonal composition root."""
    resolved_settings = settings or load_settings()
    owns_connection = connection is None
    container = build_container(resolved_settings, connection=connection)

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
        yield
        if owns_connection:
            container.connection.close()

    app = FastAPI(
        title=resolved_settings.app_title,
        description=resolved_settings.app_description,
        version=resolved_settings.app_version,
        lifespan=lifespan,
    )

    app.state.settings = resolved_settings
    app.state.container = container
    app.state.connection = container.connection

    register_exception_handlers(app)
    _mount_presentation_routers(app)

    @app.get("/", tags=["Status"])
    def root() -> dict[str, str]:
        return {"status": "online", "app": resolved_settings.app_title}

    @app.get("/health", tags=["Status"])
    def health() -> dict[str, str]:
        return {"status": "healthy"}

    return app


__all__ = ["Container", "build_container", "create_app"]
