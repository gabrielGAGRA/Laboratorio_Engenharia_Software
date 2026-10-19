"""Unit tests for Pydantic presentation schemas and validation boundaries."""

import pytest
from pydantic import ValidationError

from app.presentation.schemas import (
    ActionSuccessResponse,
    ChangeInteractionRequest,
    CreateJamRequest,
    DeckPlaylistRequest,
    ExecutiveDashboardResponse,
    InteractionRequest,
    JoinJamRequest,
    PublishReviewRequest,
    RegisterUserRequest,
    TrackSearchQuery,
    UpdateProfileRequest,
    VoteJamTrackRequest,
)


def test_register_user_request_valid_payload() -> None:
    req = RegisterUserRequest(
        email="frog@ribbit.com",
        password="secretpassword",
        display_name="Ribbit User",
        age=18,
    )
    assert req.email == "frog@ribbit.com"
    assert req.plan_id is None


@pytest.mark.parametrize(
    ("password", "display_name", "age"),
    [
        ("12345", "Valid Name", 20),
        ("validpass", "A", 20),
        ("validpass", "X" * 51, 20),
        ("validpass", "Valid Name", -1),
    ],
)
def test_register_user_request_rejects_invalid_fields(
    password: str,
    display_name: str,
    age: int,
) -> None:
    with pytest.raises(ValidationError):
        RegisterUserRequest(
            email="frog@ribbit.com",
            password=password,
            display_name=display_name,
            age=age,
        )


def test_interaction_request_accepts_only_valid_literals() -> None:
    for action in ("like", "superlike", "dislike"):
        req = InteractionRequest(user_id=1, track_id=2, action=action)  # type: ignore[arg-type]
        assert req.action == action

    with pytest.raises(ValidationError):
        InteractionRequest(user_id=1, track_id=2, action="love")  # type: ignore[arg-type]


def test_change_interaction_request_rejects_invalid_action() -> None:
    with pytest.raises(ValidationError):
        ChangeInteractionRequest(user_id=1, track_id=2, new_action="skip")  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("limit", "offset"),
    [
        (0, 0),
        (101, 0),
        (20, -1),
    ],
)
def test_track_search_query_enforces_pagination_bounds(limit: int, offset: int) -> None:
    with pytest.raises(ValidationError):
        TrackSearchQuery(limit=limit, offset=offset)


def test_create_jam_request_enforces_room_name_length() -> None:
    with pytest.raises(ValidationError):
        CreateJamRequest(host_user_id=1, room_name="")

    with pytest.raises(ValidationError):
        CreateJamRequest(host_user_id=1, room_name="R" * 101)


def test_join_jam_request_enforces_room_code_length() -> None:
    with pytest.raises(ValidationError):
        JoinJamRequest(room_code="")

    with pytest.raises(ValidationError):
        JoinJamRequest(room_code="C" * 21)


@pytest.mark.parametrize("points", [0, -1, 11])
def test_vote_jam_track_request_enforces_points_bounds(points: int) -> None:
    with pytest.raises(ValidationError):
        VoteJamTrackRequest(user_id=1, track_id=10, points=points)


@pytest.mark.parametrize(
    ("name", "duration_minutes", "year", "description"),
    [
        ("", 30, 2020, "ok"),
        ("X" * 101, 30, 2020, "ok"),
        ("Valid", 0, 2020, "ok"),
        ("Valid", 601, 2020, "ok"),
        ("Valid", 30, 1899, "ok"),
        ("Valid", 30, 2101, "ok"),
        ("Valid", 30, 2020, "D" * 501),
    ],
)
def test_deck_playlist_request_enforces_field_constraints(
    name: str,
    duration_minutes: int | None,
    year: int | None,
    description: str | None,
) -> None:
    with pytest.raises(ValidationError):
        DeckPlaylistRequest(
            user_id=1,
            name=name,
            duration_minutes=duration_minutes,
            year=year,
            description=description,
        )


@pytest.mark.parametrize(
    ("display_name", "new_password"),
    [
        ("A", None),
        ("N" * 51, None),
        (None, "12345"),
    ],
)
def test_update_profile_request_enforces_min_and_max_lengths(
    display_name: str | None,
    new_password: str | None,
) -> None:
    with pytest.raises(ValidationError):
        UpdateProfileRequest(
            display_name=display_name,
            new_password=new_password,
        )


@pytest.mark.parametrize(
    ("rating", "text"),
    [
        (0, "Too low"),
        (6, "Too high"),
        (5, "T" * 1001),
    ],
)
def test_publish_review_request_enforces_rating_and_text_bounds(
    rating: int,
    text: str | None,
) -> None:
    with pytest.raises(ValidationError):
        PublishReviewRequest(
            user_id=1,
            track_id=10,
            rating=rating,
            text=text,
        )


def test_default_factory_fields_in_responses() -> None:
    action_res = ActionSuccessResponse()
    assert action_res.success is True

    dashboard_res = ExecutiveDashboardResponse(
        total_users=0,
        estimated_net_revenue=0.0,
    )
    assert dashboard_res.users_by_plan == {}
    assert dashboard_res.revenue_by_plan == {}
