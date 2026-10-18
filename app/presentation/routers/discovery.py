"""Discovery and swipe interaction router."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.application.commands import RecordSwipeCommand
from app.application.use_cases.discovery import (
    GetNextDiscoveryTrackUseCase,
    RecordSwipeInteractionUseCase,
)
from app.domain.models.interaction import InteractionAction
from app.presentation.dependencies import (
    get_next_discovery_track_use_case,
    get_record_swipe_interaction_use_case,
)
from app.presentation.schemas import (
    InteractionRequest,
    InteractionResponse,
    TrackResponse,
)

router = APIRouter(prefix="/api/discovery", tags=["Discovery"])


@router.get("/next", response_model=TrackResponse | None)
def get_next_track(
    user_id: Annotated[int, Query()],
    use_case: Annotated[
        GetNextDiscoveryTrackUseCase, Depends(get_next_discovery_track_use_case)
    ],
) -> TrackResponse | None:
    track = use_case.execute(user_id=user_id)
    if not track:
        return None
    return TrackResponse.model_validate(track)


@router.post("/interact", response_model=InteractionResponse)
def record_interaction(
    req: InteractionRequest,
    use_case: Annotated[
        RecordSwipeInteractionUseCase,
        Depends(get_record_swipe_interaction_use_case),
    ],
) -> InteractionResponse:
    action = InteractionAction(req.action.lower())
    interaction = use_case.execute(
        RecordSwipeCommand(
            user_id=req.user_id,
            track_id=req.track_id,
            action=action,
        )
    )
    return InteractionResponse.model_validate(interaction)


__all__ = ["router"]
