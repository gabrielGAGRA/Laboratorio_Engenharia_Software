"""Unit tests for SQLite repositories implementing domain/application ports."""

import sqlite3

import pytest

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
