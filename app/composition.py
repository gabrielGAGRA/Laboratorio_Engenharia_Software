"""Composition root: inlines infrastructure, use case construction, and router mounting."""

import sqlite3
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import TYPE_CHECKING, Annotated, Any

from fastapi import Depends, FastAPI

from app.application.use_cases.admin.block_track import BlockTrackUseCase
from app.application.use_cases.admin.get_audience_report import (
    GetAudienceReportUseCase,
)
from app.application.use_cases.admin.get_audit_logs import GetAuditLogsUseCase
from app.application.use_cases.admin.get_executive_dashboard import (
    GetExecutiveDashboardUseCase,
)
from app.application.use_cases.admin.get_top_moderation_reviews import (
    GetTopModerationReviewsUseCase,
)
from app.application.use_cases.admin.list_users_with_plans import (
    ListUsersWithPlansUseCase,
)
from app.application.use_cases.admin.promote_user_to_admin import (
    PromoteUserToAdminUseCase,
)
from app.application.use_cases.admin.update_subscription_plan import (
    UpdateSubscriptionPlanUseCase,
)
from app.application.use_cases.admin.update_track_explicit_flag import (
    UpdateTrackExplicitFlagUseCase,
)
from app.application.use_cases.auth.authenticate_admin import (
    AuthenticateAdminUseCase,
)
from app.application.use_cases.auth.authenticate_user import (
    AuthenticateUserUseCase,
)
from app.application.use_cases.auth.register_user import RegisterUserUseCase
from app.application.use_cases.discovery.get_next_discovery_track import (
    GetNextDiscoveryTrackUseCase,
)
from app.application.use_cases.discovery.record_swipe_interaction import (
    RecordSwipeInteractionUseCase,
)
from app.application.use_cases.jam.advance_jam_playback import (
    AdvanceJamPlaybackUseCase,
)
from app.application.use_cases.jam.create_jam import CreateJamUseCase
from app.application.use_cases.jam.get_jam_state import GetJamStateUseCase
from app.application.use_cases.jam.join_jam import JoinJamUseCase
from app.application.use_cases.jam.vote_jam_track import VoteJamTrackUseCase
from app.application.use_cases.jam.vote_skip_jam_track import (
    VoteSkipJamTrackUseCase,
)
from app.application.use_cases.playlist.add_track_to_playlist import (
    AddTrackToPlaylistUseCase,
)
from app.application.use_cases.playlist.create_deck_playlist import (
    CreateDeckPlaylistUseCase,
)
from app.application.use_cases.playlist.export_playlist_to_spotify import (
    ExportPlaylistToSpotifyUseCase,
)
from app.application.use_cases.playlist.list_user_playlists import (
    ListUserPlaylistsUseCase,
)
from app.application.use_cases.review.get_community_feed import (
    GetCommunityFeedUseCase,
)
from app.application.use_cases.review.get_track_reviews import (
    GetTrackReviewsUseCase,
)
from app.application.use_cases.review.like_review_comment import (
    LikeReviewCommentUseCase,
)
from app.application.use_cases.review.publish_review import PublishReviewUseCase
from app.application.use_cases.review.search_tracks import SearchTracksUseCase
from app.application.use_cases.user.add_family_member import (
    AddFamilyMemberUseCase,
)
from app.application.use_cases.user.cancel_subscription_plan import (
    CancelSubscriptionPlanUseCase,
)
from app.application.use_cases.user.change_subscription_plan import (
    ChangeSubscriptionPlanUseCase,
)
from app.application.use_cases.user.change_track_interaction import (
    ChangeTrackInteractionUseCase,
)
from app.application.use_cases.user.delete_user_account import (
    DeleteUserAccountUseCase,
)
from app.application.use_cases.user.get_annual_stats import (
    GetAnnualListeningStatsUseCase,
)
from app.application.use_cases.user.get_user_profile import (
    GetUserProfileUseCase,
)
from app.application.use_cases.user.link_spotify_account import (
    LinkSpotifyAccountUseCase,
)
from app.application.use_cases.user.list_blocked_genres import (
    ListBlockedGenresUseCase,
)
from app.application.use_cases.user.list_family_members import (
    ListFamilyMembersUseCase,
)
from app.application.use_cases.user.list_plans import ListPlansUseCase
from app.application.use_cases.user.list_user_interactions import (
    ListUserInteractionsUseCase,
)
from app.application.use_cases.user.remove_family_member import (
    RemoveFamilyMemberUseCase,
)
from app.application.use_cases.user.update_blocked_genres import (
    UpdateBlockedGenresUseCase,
)
from app.application.use_cases.user.update_profile import UpdateProfileUseCase
from app.config import Settings, load_settings
from app.domain.exceptions import PermissionDeniedError
from app.infrastructure.adapters.music_service import (
    ExternalMusicServiceAdapter,
)
from app.infrastructure.adapters.security.password_hasher import (
    PBKDF2PasswordHasher,
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
from app.infrastructure.adapters.sqlite.setup import SCHEMA_PATH
from app.presentation.dependencies import (
    get_add_family_member_use_case,
    get_add_track_to_playlist_use_case,
    get_admin_id,
    get_advance_jam_playback_use_case,
    get_annual_stats_use_case,
    get_audience_report_use_case,
    get_audit_logs_use_case,
    get_authenticate_admin_use_case,
    get_authenticate_user_use_case,
    get_block_track_use_case,
    get_cancel_subscription_plan_use_case,
    get_change_subscription_plan_use_case,
    get_change_track_interaction_use_case,
    get_community_feed_use_case,
    get_create_deck_playlist_use_case,
    get_create_jam_use_case,
    get_delete_user_account_use_case,
    get_executive_dashboard_use_case,
    get_export_playlist_to_spotify_use_case,
    get_jam_state_use_case,
    get_join_jam_use_case,
    get_like_review_comment_use_case,
    get_link_spotify_account_use_case,
    get_list_blocked_genres_use_case,
    get_list_family_members_use_case,
    get_list_plans_use_case,
    get_list_user_interactions_use_case,
    get_list_user_playlists_use_case,
    get_list_users_with_plans_use_case,
    get_next_discovery_track_use_case,
    get_promote_user_to_admin_use_case,
    get_publish_review_use_case,
    get_record_swipe_interaction_use_case,
    get_register_user_use_case,
    get_remove_family_member_use_case,
    get_search_tracks_use_case,
    get_top_moderation_reviews_use_case,
    get_track_reviews_use_case,
    get_update_blocked_genres_use_case,
    get_update_profile_use_case,
    get_update_subscription_plan_use_case,
    get_update_track_explicit_flag_use_case,
    get_user_profile_use_case,
    get_vote_jam_track_use_case,
    get_vote_skip_jam_track_use_case,
    require_admin,
)
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

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


@dataclass(slots=True, kw_only=True)
class Container:
    """Dependency injection container holding application adapters and use cases."""

    settings: Settings
    connection: sqlite3.Connection
    password_hasher: PBKDF2PasswordHasher
    music_service: ExternalMusicServiceAdapter
    user_repo: SQLiteUserRepository
    plan_repo: SQLitePlanRepository
    track_repo: SQLiteTrackRepository
    playlist_repo: SQLitePlaylistRepository
    interaction_repo: SQLiteInteractionRepository
    jam_repo: SQLiteJamRepository
    review_repo: SQLiteReviewRepository
    # Auth
    register_user: RegisterUserUseCase
    authenticate_user: AuthenticateUserUseCase
    authenticate_admin: AuthenticateAdminUseCase
    # Discovery
    get_next_discovery_track: GetNextDiscoveryTrackUseCase
    record_swipe_interaction: RecordSwipeInteractionUseCase
    # Playlist
    create_deck_playlist: CreateDeckPlaylistUseCase
    add_track_to_playlist: AddTrackToPlaylistUseCase
    export_playlist_to_spotify: ExportPlaylistToSpotifyUseCase
    list_user_playlists: ListUserPlaylistsUseCase
    # Jam
    create_jam: CreateJamUseCase
    join_jam: JoinJamUseCase
    get_jam_state: GetJamStateUseCase
    vote_jam_track: VoteJamTrackUseCase
    vote_skip_jam_track: VoteSkipJamTrackUseCase
    advance_jam_playback: AdvanceJamPlaybackUseCase
    # Review
    search_tracks: SearchTracksUseCase
    publish_review: PublishReviewUseCase
    get_track_reviews: GetTrackReviewsUseCase
    get_community_feed: GetCommunityFeedUseCase
    like_review_comment: LikeReviewCommentUseCase
    # User
    get_user_profile: GetUserProfileUseCase
    update_profile: UpdateProfileUseCase
    delete_user_account: DeleteUserAccountUseCase
    list_plans: ListPlansUseCase
    change_subscription_plan: ChangeSubscriptionPlanUseCase
    cancel_subscription_plan: CancelSubscriptionPlanUseCase
    add_family_member: AddFamilyMemberUseCase
    remove_family_member: RemoveFamilyMemberUseCase
    list_family_members: ListFamilyMembersUseCase
    list_blocked_genres: ListBlockedGenresUseCase
    update_blocked_genres: UpdateBlockedGenresUseCase
    list_user_interactions: ListUserInteractionsUseCase
    change_track_interaction: ChangeTrackInteractionUseCase
    get_annual_listening_stats: GetAnnualListeningStatsUseCase
    link_spotify_account: LinkSpotifyAccountUseCase
    # Admin
    get_executive_dashboard: GetExecutiveDashboardUseCase
    list_users_with_plans: ListUsersWithPlansUseCase
    update_subscription_plan: UpdateSubscriptionPlanUseCase
    update_track_explicit_flag: UpdateTrackExplicitFlagUseCase
    block_track: BlockTrackUseCase
    get_top_moderation_reviews: GetTopModerationReviewsUseCase
    get_audience_report: GetAudienceReportUseCase
    get_audit_logs: GetAuditLogsUseCase
    promote_user_to_admin: PromoteUserToAdminUseCase


def _seed_default_plans(conn: sqlite3.Connection) -> None:
    """Seeds baseline subscription plans required by user registration."""
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM plans WHERE name = 'Free'")
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO plans (name, monthly_price, max_profiles) VALUES"
                " (?, ?, ?)",
                ("Free", 0.0, 1),
            )
            cursor.execute(
                "INSERT INTO plans (name, monthly_price, max_profiles) VALUES"
                " (?, ?, ?)",
                ("Premium", 19.90, 1),
            )
            cursor.execute(
                "INSERT INTO plans (name, monthly_price, max_profiles) VALUES"
                " (?, ?, ?)",
                ("Family", 34.90, 6),
            )
            conn.commit()
    finally:
        cursor.close()


def build_container(
    settings: Settings,
    connection: sqlite3.Connection | None = None,
) -> Container:
    if connection is not None:
        conn = connection
    else:
        conn = sqlite3.connect(settings.database_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
    password_hasher = PBKDF2PasswordHasher(iterations=settings.password_hash_iterations)
    music_service = ExternalMusicServiceAdapter(spotify_token=settings.spotify_token)

    user_repo = SQLiteUserRepository(conn)
    plan_repo = SQLitePlanRepository(conn)
    track_repo = SQLiteTrackRepository(conn)
    playlist_repo = SQLitePlaylistRepository(conn)
    interaction_repo = SQLiteInteractionRepository(conn)
    jam_repo = SQLiteJamRepository(conn)
    review_repo = SQLiteReviewRepository(conn)

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
        # Auth
        register_user=RegisterUserUseCase(user_repo, plan_repo, password_hasher),
        authenticate_user=AuthenticateUserUseCase(user_repo, password_hasher),
        authenticate_admin=AuthenticateAdminUseCase(user_repo, password_hasher),
        # Discovery
        get_next_discovery_track=GetNextDiscoveryTrackUseCase(
            user_repo, track_repo, interaction_repo
        ),
        record_swipe_interaction=RecordSwipeInteractionUseCase(
            user_repo, track_repo, interaction_repo
        ),
        # Playlist
        create_deck_playlist=CreateDeckPlaylistUseCase(
            user_repo, track_repo, playlist_repo
        ),
        add_track_to_playlist=AddTrackToPlaylistUseCase(
            user_repo, track_repo, playlist_repo
        ),
        export_playlist_to_spotify=ExportPlaylistToSpotifyUseCase(
            user_repo, playlist_repo, music_service
        ),
        list_user_playlists=ListUserPlaylistsUseCase(user_repo, playlist_repo),
        # Jam
        create_jam=CreateJamUseCase(jam_repo, user_repo),
        join_jam=JoinJamUseCase(jam_repo),
        get_jam_state=GetJamStateUseCase(jam_repo, user_repo, track_repo),
        vote_jam_track=VoteJamTrackUseCase(jam_repo, user_repo, track_repo),
        vote_skip_jam_track=VoteSkipJamTrackUseCase(jam_repo, user_repo, track_repo),
        advance_jam_playback=AdvanceJamPlaybackUseCase(jam_repo),
        # Review
        search_tracks=SearchTracksUseCase(user_repo, track_repo),
        publish_review=PublishReviewUseCase(user_repo, track_repo, review_repo),
        get_track_reviews=GetTrackReviewsUseCase(track_repo, review_repo),
        get_community_feed=GetCommunityFeedUseCase(review_repo),
        like_review_comment=LikeReviewCommentUseCase(review_repo),
        # User
        get_user_profile=GetUserProfileUseCase(user_repo, plan_repo),
        update_profile=UpdateProfileUseCase(user_repo, password_hasher),
        delete_user_account=DeleteUserAccountUseCase(user_repo),
        list_plans=ListPlansUseCase(plan_repo),
        change_subscription_plan=ChangeSubscriptionPlanUseCase(user_repo, plan_repo),
        cancel_subscription_plan=CancelSubscriptionPlanUseCase(user_repo, plan_repo),
        add_family_member=AddFamilyMemberUseCase(user_repo, plan_repo),
        remove_family_member=RemoveFamilyMemberUseCase(user_repo, plan_repo),
        list_family_members=ListFamilyMembersUseCase(user_repo),
        list_blocked_genres=ListBlockedGenresUseCase(user_repo),
        update_blocked_genres=UpdateBlockedGenresUseCase(user_repo, plan_repo),
        list_user_interactions=ListUserInteractionsUseCase(user_repo, interaction_repo),
        change_track_interaction=ChangeTrackInteractionUseCase(
            user_repo, plan_repo, interaction_repo
        ),
        get_annual_listening_stats=GetAnnualListeningStatsUseCase(
            user_repo, plan_repo, interaction_repo
        ),
        link_spotify_account=LinkSpotifyAccountUseCase(user_repo),
        # Admin
        get_executive_dashboard=GetExecutiveDashboardUseCase(user_repo, plan_repo),
        list_users_with_plans=ListUsersWithPlansUseCase(user_repo, plan_repo),
        update_subscription_plan=UpdateSubscriptionPlanUseCase(plan_repo),
        update_track_explicit_flag=UpdateTrackExplicitFlagUseCase(track_repo),
        block_track=BlockTrackUseCase(track_repo),
        get_top_moderation_reviews=GetTopModerationReviewsUseCase(review_repo),
        get_audience_report=GetAudienceReportUseCase(user_repo, track_repo),
        get_audit_logs=GetAuditLogsUseCase(),
        promote_user_to_admin=PromoteUserToAdminUseCase(user_repo),
    )


def setup_dependency_overrides(app: FastAPI, container: Container) -> None:
    """Configures FastAPI dependency overrides to inject container use cases and repositories."""
    # 1. Direct presentation provider mappings
    provider_map: dict[Any, Any] = {
        get_authenticate_admin_use_case: container.authenticate_admin,
        get_authenticate_user_use_case: container.authenticate_user,
        get_register_user_use_case: container.register_user,
        get_next_discovery_track_use_case: container.get_next_discovery_track,
        get_record_swipe_interaction_use_case: container.record_swipe_interaction,
        get_create_deck_playlist_use_case: container.create_deck_playlist,
        get_add_track_to_playlist_use_case: container.add_track_to_playlist,
        get_list_user_playlists_use_case: container.list_user_playlists,
        get_export_playlist_to_spotify_use_case: container.export_playlist_to_spotify,
        get_create_jam_use_case: container.create_jam,
        get_join_jam_use_case: container.join_jam,
        get_jam_state_use_case: container.get_jam_state,
        get_vote_jam_track_use_case: container.vote_jam_track,
        get_vote_skip_jam_track_use_case: container.vote_skip_jam_track,
        get_advance_jam_playback_use_case: container.advance_jam_playback,
        get_search_tracks_use_case: container.search_tracks,
        get_publish_review_use_case: container.publish_review,
        get_community_feed_use_case: container.get_community_feed,
        get_like_review_comment_use_case: container.like_review_comment,
        get_track_reviews_use_case: container.get_track_reviews,
        get_executive_dashboard_use_case: container.get_executive_dashboard,
        get_list_users_with_plans_use_case: container.list_users_with_plans,
        get_audience_report_use_case: container.get_audience_report,
        get_block_track_use_case: container.block_track,
        get_update_track_explicit_flag_use_case: container.update_track_explicit_flag,
        get_promote_user_to_admin_use_case: container.promote_user_to_admin,
        get_update_subscription_plan_use_case: container.update_subscription_plan,
        get_top_moderation_reviews_use_case: container.get_top_moderation_reviews,
        get_audit_logs_use_case: container.get_audit_logs,
        get_user_profile_use_case: container.get_user_profile,
        get_update_profile_use_case: container.update_profile,
        get_link_spotify_account_use_case: container.link_spotify_account,
        get_list_plans_use_case: container.list_plans,
        get_change_subscription_plan_use_case: container.change_subscription_plan,
        get_cancel_subscription_plan_use_case: container.cancel_subscription_plan,
        get_delete_user_account_use_case: container.delete_user_account,
        get_annual_stats_use_case: container.get_annual_listening_stats,
        get_change_track_interaction_use_case: container.change_track_interaction,
        get_list_user_interactions_use_case: container.list_user_interactions,
        get_list_blocked_genres_use_case: container.list_blocked_genres,
        get_update_blocked_genres_use_case: container.update_blocked_genres,
        get_list_family_members_use_case: container.list_family_members,
        get_add_family_member_use_case: container.add_family_member,
        get_remove_family_member_use_case: container.remove_family_member,
    }

    def _make_override(target: Any) -> Any:
        return lambda: target

    for provider_fn, instance in provider_map.items():
        app.dependency_overrides[provider_fn] = _make_override(instance)

    # 2. Admin credential verification override
    def _override_require_admin(
        admin_id: Annotated[int, Depends(get_admin_id)],
    ) -> int:
        admin_user = container.user_repo.find_by_id(admin_id)
        if not admin_user or not admin_user.is_admin:
            raise PermissionDeniedError("Access restricted to administrators.")
        return admin_id

    app.dependency_overrides[require_admin] = _override_require_admin


def _mount_presentation_routers(app: FastAPI) -> None:
    """Mounts all presentation-layer routers."""
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
    async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
        if SCHEMA_PATH.exists():
            schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
            container.connection.executescript(schema_sql)
            container.connection.commit()
            _seed_default_plans(container.connection)

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

    setup_dependency_overrides(app, container)
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
