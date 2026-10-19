"""Unit tests for discovery router functions."""

from unittest.mock import MagicMock

from app.application.commands import RecordSwipeCommand
from app.application.use_cases.discovery import (
    GetNextDiscoveryTrackUseCase,
    RecordSwipeInteractionUseCase,
)
from app.domain.models import Interaction, InteractionAction, Track
from app.presentation.routers.discovery import (
    get_next_track,
    record_interaction,
)
from app.presentation.schemas import InteractionRequest


def test_get_next_track_returns_track_response_when_available() -> None:
    mock_use_case = MagicMock(spec=GetNextDiscoveryTrackUseCase)
    track = Track(
        track_id=15,
        title="Lilypad Groove",
        artist="DJ Toad",
        duration_seconds=195,
        genre="electronic",
    )
    mock_use_case.execute.return_value = track

    res = get_next_track(user_id=9, use_case=mock_use_case)

    assert res is not None
    assert res.track_id == 15
    assert res.title == "Lilypad Groove"
    mock_use_case.execute.assert_called_once_with(user_id=9)


def test_get_next_track_returns_none_when_catalog_exhausted() -> None:
    mock_use_case = MagicMock(spec=GetNextDiscoveryTrackUseCase)
    mock_use_case.execute.return_value = None

    res = get_next_track(user_id=9, use_case=mock_use_case)

    assert res is None
    mock_use_case.execute.assert_called_once_with(user_id=9)


def test_record_interaction_converts_action_and_returns_response() -> None:
    mock_use_case = MagicMock(spec=RecordSwipeInteractionUseCase)
    interaction = Interaction(
        interaction_id=44,
        user_id=9,
        track_id=15,
        action=InteractionAction.SUPERLIKE,
    )
    mock_use_case.execute.return_value = interaction
    req = InteractionRequest(user_id=9, track_id=15, action="superlike")

    res = record_interaction(req=req, use_case=mock_use_case)

    assert res.interaction_id == 44
    assert res.user_id == 9
    assert res.track_id == 15
    assert res.action == "superlike"
    mock_use_case.execute.assert_called_once_with(
        RecordSwipeCommand(
            user_id=9,
            track_id=15,
            action=InteractionAction.SUPERLIKE,
        )
    )
