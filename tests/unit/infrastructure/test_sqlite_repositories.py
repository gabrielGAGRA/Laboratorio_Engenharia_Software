"""Unit tests for SQLite repositories implementing domain/application ports."""

import sqlite3

import pytest

from app.domain.exceptions import EntityNotFoundError
from app.domain.models import (
    Interaction,
    InteractionAction,
    Jam,
    JamQueueItem,
    Plan,
    Playlist,
    ReviewComment,
    Track,
    User,
)
from app.infrastructure.persistence.connection import SCHEMA_PATH
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


@pytest.fixture
def conn() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON;")
    connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    connection.commit()
    yield connection
    connection.close()


def test_user_and_plan_repositories(conn: sqlite3.Connection) -> None:
    plan_repo = SQLitePlanRepository(conn)
    user_repo = SQLiteUserRepository(conn)

    plan = Plan(name="Family", initial_monthly_price=29.90, initial_max_profiles=6)
    saved_plan = plan_repo.save(plan)
    assert saved_plan.plan_id is not None
    assert plan_repo.find_by_id(saved_plan.plan_id) is not None
    assert plan_repo.find_by_name("Family") is not None

    user = User(
        email="john@example.com",
        password_hash="hashed_pw",
        display_name="John Doe",
        age=25,
        plan_id=saved_plan.plan_id,
        blocked_genres=frozenset({"metal"}),
    )
    saved_user = user_repo.save(user)
    assert saved_user.user_id is not None
    assert saved_user.blocked_genres == frozenset({"metal"})

    found_user = user_repo.find_by_email("JOHN@example.com")
    assert found_user is not None
    assert found_user.user_id == saved_user.user_id

    dependent = User(
        email="dep@example.com",
        password_hash="hashed_pw",
        display_name="Dep Doe",
        age=12,
        plan_id=saved_plan.plan_id,
        primary_account_id=saved_user.user_id,
    )
    saved_dep = user_repo.save(dependent)
    assert saved_dep.user_id is not None

    dependents = user_repo.list_dependents(saved_user.user_id)
    assert len(dependents) == 1
    assert dependents[0].email == "dep@example.com"

    assert len(user_repo.list_all()) == 2
    assert user_repo.delete(saved_dep.user_id) is True
    assert user_repo.find_by_id(saved_dep.user_id) is None


def test_track_and_interaction_repositories(conn: sqlite3.Connection) -> None:
    plan_repo = SQLitePlanRepository(conn)
    user_repo = SQLiteUserRepository(conn)
    track_repo = SQLiteTrackRepository(conn)
    interaction_repo = SQLiteInteractionRepository(conn)

    plan = plan_repo.save(
        Plan(name="Free", initial_monthly_price=0.0, initial_max_profiles=1)
    )
    user = user_repo.save(
        User(
            email="jane@example.com",
            password_hash="pw",
            display_name="Jane",
            age=20,
            plan_id=plan.plan_id,
        )
    )

    t1 = track_repo.save(
        Track(
            title="Bohemian Rhapsody",
            artist="Queen",
            duration_seconds=354,
            genre="Rock",
            explicit=False,
        )
    )
    _ = track_repo.save(
        Track(
            title="Rap God",
            artist="Eminem",
            duration_seconds=363,
            genre="Hip Hop",
            explicit=True,
        )
    )

    assert track_repo.count_all() == 2
    active_clean = track_repo.list_active(limit=10, block_explicit=True)
    assert len(active_clean) == 1
    assert active_clean[0].track_id == t1.track_id

    filtered = track_repo.find_by_filters(artist="queen")
    assert len(filtered) == 1
    assert filtered[0].title == "Bohemian Rhapsody"

    interaction = Interaction(
        user_id=user.user_id,
        track_id=t1.track_id,
        action=InteractionAction.LIKE,
    )
    saved_interaction = interaction_repo.save(interaction)
    assert saved_interaction.is_positive is True

    interacted_ids = interaction_repo.list_interacted_track_ids(user.user_id)
    assert interacted_ids == [t1.track_id]

    by_user = interaction_repo.list_by_user(user.user_id, action=InteractionAction.LIKE)
    assert len(by_user) == 1


def test_playlist_repository_aggregate(conn: sqlite3.Connection) -> None:
    plan_repo = SQLitePlanRepository(conn)
    user_repo = SQLiteUserRepository(conn)
    track_repo = SQLiteTrackRepository(conn)
    playlist_repo = SQLitePlaylistRepository(conn)

    plan = plan_repo.save(Plan(name="Solo", initial_monthly_price=10.0))
    user = user_repo.save(
        User(
            email="bob@example.com",
            password_hash="pw",
            display_name="Bob",
            age=30,
            plan_id=plan.plan_id,
        )
    )
    track = track_repo.save(
        Track(
            title="Song A",
            artist="Artist A",
            duration_seconds=200,
            genre="Pop",
        )
    )

    playlist = Playlist(
        user_id=user.user_id,
        name="Favorites",
        description="My best tracks",
        initial_tracks=[track],
    )
    saved_playlist = playlist_repo.save(playlist)
    assert saved_playlist.playlist_id is not None
    assert len(saved_playlist.tracks) == 1
    assert saved_playlist.tracks[0].track_id == track.track_id

    loaded = playlist_repo.find_by_id(saved_playlist.playlist_id)
    assert loaded is not None
    assert len(loaded.tracks) == 1
    assert loaded.tracks[0].title == "Song A"

    user_playlists = playlist_repo.list_by_user(user.user_id)
    assert len(user_playlists) == 1
    assert len(user_playlists[0].tracks) == 1


def test_jam_and_review_repositories(conn: sqlite3.Connection) -> None:
    plan_repo = SQLitePlanRepository(conn)
    user_repo = SQLiteUserRepository(conn)
    track_repo = SQLiteTrackRepository(conn)
    jam_repo = SQLiteJamRepository(conn)
    review_repo = SQLiteReviewRepository(conn)

    plan = plan_repo.save(Plan(name="PlanJam", initial_monthly_price=0.0))
    user = user_repo.save(
        User(
            email="host@example.com",
            password_hash="pw",
            display_name="Host",
            age=22,
            plan_id=plan.plan_id,
        )
    )
    track = track_repo.save(
        Track(
            title="Track Jam",
            artist="Jammer",
            duration_seconds=180,
            genre="Indie",
        )
    )

    jam = Jam(host_user_id=user.user_id, room_name="Rock Party")
    saved_jam = jam_repo.save(jam)
    assert saved_jam.jam_id is not None
    assert jam_repo.find_by_code(saved_jam.room_code) is not None

    q_item = JamQueueItem(
        jam_id=saved_jam.jam_id,
        track_id=track.track_id,
        initial_vote_points=3,
    )
    saved_q = jam_repo.save_queue_item(q_item)
    assert saved_q.vote_points == 3

    queue = jam_repo.list_queue(saved_jam.jam_id)
    assert len(queue) == 1
    assert queue[0].track_id == track.track_id

    assert jam_repo.remove_track_from_queue(saved_jam.jam_id, track.track_id) is True
    assert len(jam_repo.list_queue(saved_jam.jam_id)) == 0

    review = ReviewComment(
        user_id=user.user_id,
        track_id=track.track_id,
        initial_rating=5,
        text="Masterpiece!",
        initial_likes_count=10,
    )
    saved_review = review_repo.save(review)
    assert saved_review.review_id is not None
    assert saved_review.rating == 5

    reviews_for_track = review_repo.list_by_track(track.track_id, limit=5)
    assert len(reviews_for_track) == 1
    assert reviews_for_track[0].text == "Masterpiece!"

    top_recent = review_repo.list_top_recent(days=7, limit=3)
    assert len(top_recent) == 1
    assert top_recent[0].likes_count == 10

    assert review_repo.has_user_liked(saved_review.review_id, user.user_id) is False
    review_repo.record_like(saved_review.review_id, user.user_id)
    assert review_repo.has_user_liked(saved_review.review_id, user.user_id) is True
    # Idempotency of record_like
    review_repo.record_like(saved_review.review_id, user.user_id)
    assert review_repo.has_user_liked(saved_review.review_id, user.user_id) is True


def test_interaction_repository_atomic_upsert(conn: sqlite3.Connection) -> None:
    plan_repo = SQLitePlanRepository(conn)
    user_repo = SQLiteUserRepository(conn)
    track_repo = SQLiteTrackRepository(conn)
    interaction_repo = SQLiteInteractionRepository(conn)

    plan = plan_repo.save(Plan(name="FreePlan", initial_monthly_price=0.0))
    user = user_repo.save(
        User(
            email="upsert@test.com",
            password_hash="pw",
            display_name="Upsert",
            age=20,
            plan_id=plan.plan_id,
        )
    )
    track = track_repo.save(
        Track(title="Song", artist="Art", duration_seconds=120, genre="Pop")
    )

    i1 = interaction_repo.save(
        Interaction(
            user_id=user.user_id,
            track_id=track.track_id,
            action=InteractionAction.LIKE,
        )
    )
    assert i1.action == InteractionAction.LIKE
    assert i1.interaction_id is not None

    i2 = interaction_repo.save(
        Interaction(
            user_id=user.user_id,
            track_id=track.track_id,
            action=InteractionAction.DISLIKE,
        )
    )
    assert i2.interaction_id == i1.interaction_id
    assert i2.action == InteractionAction.DISLIKE

    cursor = conn.execute(
        "SELECT * FROM interactions WHERE user_id = ? AND track_id = ?",
        (user.user_id, track.track_id),
    )
    rows = cursor.fetchall()
    assert len(rows) == 1
    assert rows[0]["action"] == InteractionAction.DISLIKE.value


def test_repositories_raise_entity_not_found_on_missing_id(
    conn: sqlite3.Connection,
) -> None:
    plan_repo = SQLitePlanRepository(conn)
    user_repo = SQLiteUserRepository(conn)
    track_repo = SQLiteTrackRepository(conn)
    jam_repo = SQLiteJamRepository(conn)
    playlist_repo = SQLitePlaylistRepository(conn)
    review_repo = SQLiteReviewRepository(conn)

    with pytest.raises(EntityNotFoundError) as exc_info:
        plan_repo.save(Plan(plan_id=9999, name="Missing", initial_monthly_price=5.0))
    assert exc_info.value.details.get("entity_name") == "Plan"

    with pytest.raises(EntityNotFoundError) as exc_info:
        user_repo.save(
            User(
                user_id=9999,
                email="missing@x.com",
                password_hash="pw",
                display_name="Miss",
                age=20,
                plan_id=1,
            )
        )
    assert exc_info.value.details.get("entity_name") == "User"

    with pytest.raises(EntityNotFoundError) as exc_info:
        track_repo.save(
            Track(
                track_id=9999,
                title="Missing",
                artist="Nobody",
                duration_seconds=100,
                genre="Pop",
            )
        )
    assert exc_info.value.details.get("entity_name") == "Track"

    with pytest.raises(EntityNotFoundError) as exc_info:
        jam_repo.save(Jam(jam_id=9999, host_user_id=1, room_name="Missing"))
    assert exc_info.value.details.get("entity_name") == "Jam"

    with pytest.raises(EntityNotFoundError) as exc_info:
        playlist_repo.save(Playlist(playlist_id=9999, user_id=1, name="Missing"))
    assert exc_info.value.details.get("entity_name") == "Playlist"

    with pytest.raises(EntityNotFoundError) as exc_info:
        review_repo.save(
            ReviewComment(
                review_id=9999,
                user_id=1,
                track_id=1,
                initial_rating=3,
                text="Missing",
            )
        )
    assert exc_info.value.details.get("entity_name") == "ReviewComment"


def test_jam_repository_advance_playback_atomic(conn: sqlite3.Connection) -> None:
    plan_repo = SQLitePlanRepository(conn)
    user_repo = SQLiteUserRepository(conn)
    track_repo = SQLiteTrackRepository(conn)
    jam_repo = SQLiteJamRepository(conn)

    plan = plan_repo.save(Plan(name="PlanJamAdv", initial_monthly_price=0.0))
    user = user_repo.save(
        User(
            email="hostadv@test.com",
            password_hash="pw",
            display_name="AdvHost",
            age=25,
            plan_id=plan.plan_id,
        )
    )
    track1 = track_repo.save(
        Track(title="T1", artist="A1", duration_seconds=100, genre="Pop")
    )
    track2 = track_repo.save(
        Track(title="T2", artist="A2", duration_seconds=150, genre="Pop")
    )

    jam = jam_repo.save(Jam(host_user_id=user.user_id, room_name="JamAdv"))
    jam_repo.save_queue_item(
        JamQueueItem(
            jam_id=jam.jam_id,
            track_id=track1.track_id,
            initial_vote_points=5,
        )
    )
    jam_repo.save_queue_item(
        JamQueueItem(
            jam_id=jam.jam_id,
            track_id=track2.track_id,
            initial_vote_points=2,
        )
    )

    updated_jam = jam_repo.advance_playback(
        jam_id=jam.jam_id,
        new_track_id=track1.track_id,
        removed_track_id=track1.track_id,
    )
    assert updated_jam.current_track_id == track1.track_id

    queue = jam_repo.list_queue(jam.jam_id)
    assert len(queue) == 1
    assert queue[0].track_id == track2.track_id

    with pytest.raises(EntityNotFoundError):
        jam_repo.advance_playback(
            jam_id=9999,
            new_track_id=track2.track_id,
            removed_track_id=track2.track_id,
        )


def test_track_repository_find_by_ids(conn: sqlite3.Connection) -> None:
    track_repo = SQLiteTrackRepository(conn)

    assert track_repo.find_by_ids([]) == {}

    t1 = track_repo.save(
        Track(title="Track 1", artist="Art 1", duration_seconds=100, genre="Rock")
    )
    t2 = track_repo.save(
        Track(title="Track 2", artist="Art 2", duration_seconds=200, genre="Jazz")
    )

    tracks_map = track_repo.find_by_ids([t1.track_id, t2.track_id, 9999, t1.track_id])
    assert len(tracks_map) == 2
    assert t1.track_id in tracks_map
    assert t2.track_id in tracks_map
    assert tracks_map[t1.track_id].title == "Track 1"
    assert tracks_map[t2.track_id].title == "Track 2"


def test_counts_in_user_and_track_repositories(conn: sqlite3.Connection) -> None:
    plan_repo = SQLitePlanRepository(conn)
    user_repo = SQLiteUserRepository(conn)
    track_repo = SQLiteTrackRepository(conn)

    assert user_repo.count_all() == 0
    assert track_repo.count_all() == 0
    assert track_repo.count_active() == 0

    plan = plan_repo.save(Plan(name="CountPlan", initial_monthly_price=0.0))
    user_repo.save(
        User(
            email="u1@test.com",
            password_hash="pw",
            display_name="U1",
            age=20,
            plan_id=plan.plan_id,
        )
    )
    user_repo.save(
        User(
            email="u2@test.com",
            password_hash="pw",
            display_name="U2",
            age=25,
            plan_id=plan.plan_id,
        )
    )

    assert user_repo.count_all() == 2

    track_repo.save(
        Track(title="Active Track", artist="Art", duration_seconds=100, genre="Pop")
    )
    track_repo.save(
        Track(
            title="Deleted Track",
            artist="Art",
            duration_seconds=100,
            genre="Pop",
            is_deleted=True,
        )
    )

    assert track_repo.count_all() == 2
    assert track_repo.count_active() == 1


def test_audit_log_repository(conn: sqlite3.Connection) -> None:
    audit_repo = SQLiteAuditLogRepository(conn)
    assert audit_repo.list_all() == []

    audit_repo.log_event("EVENT_A", "SUCCESS")
    audit_repo.log_event("EVENT_B", "FAILED")

    logs = audit_repo.list_all()
    assert len(logs) == 2
    assert logs[0].event == "EVENT_A"
    assert logs[0].status == "SUCCESS"
    assert logs[1].event == "EVENT_B"
    assert logs[1].status == "FAILED"
