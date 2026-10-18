"""Collaborative Jam session and queue voting router."""

from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, Depends, Query, status

from app.application.dtos.jam_dtos import (
    CreateJamInput,
    VoteJamTrackInput,
    VoteSkipJamTrackInput,
)
from app.presentation.dependencies import (
    get_advance_jam_playback_use_case,
    get_create_jam_use_case,
    get_jam_state_use_case,
    get_join_jam_use_case,
    get_vote_jam_track_use_case,
    get_vote_skip_jam_track_use_case,
)
from app.presentation.schemas import (
    ActionSuccessResponse,
    CreateJamRequest,
    JamQueueItemResponse,
    JamResponse,
    JamStateResponse,
    JoinJamRequest,
    SkipJamTrackRequest,
    VoteJamTrackRequest,
)

if TYPE_CHECKING:
    from app.application.use_cases.jam import (
        AdvanceJamPlaybackUseCase,
        CreateJamUseCase,
        GetJamStateUseCase,
        JoinJamUseCase,
        VoteJamTrackUseCase,
        VoteSkipJamTrackUseCase,
    )

router = APIRouter(prefix="/api/jams", tags=["Collaborative Jams"])


@router.post("", response_model=JamResponse, status_code=status.HTTP_201_CREATED)
def create_jam(
    req: CreateJamRequest,
    use_case: Annotated[CreateJamUseCase, Depends(get_create_jam_use_case)],
) -> JamResponse:
    jam = use_case.execute(
        CreateJamInput(
            host_user_id=req.host_user_id,
            room_name=req.room_name,
        )
    )
    return JamResponse.model_validate(jam)


@router.post("/join", response_model=JamResponse)
def join_jam(
    req: JoinJamRequest,
    use_case: Annotated[JoinJamUseCase, Depends(get_join_jam_use_case)],
) -> JamResponse:
    jam = use_case.execute(room_code=req.room_code)
    return JamResponse.model_validate(jam)


@router.get("/{jam_id}/state", response_model=JamStateResponse)
def get_jam_state(
    jam_id: int,
    user_id: Annotated[int, Query()],
    use_case: Annotated[GetJamStateUseCase, Depends(get_jam_state_use_case)],
) -> JamStateResponse:
    state = use_case.execute(jam_id=jam_id, user_id=user_id)
    return JamStateResponse.model_validate(state)


@router.post("/{jam_id}/vote", response_model=JamQueueItemResponse)
def vote_jam_track(
    jam_id: int,
    req: VoteJamTrackRequest,
    use_case: Annotated[VoteJamTrackUseCase, Depends(get_vote_jam_track_use_case)],
) -> JamQueueItemResponse:
    queue_item = use_case.execute(
        VoteJamTrackInput(
            jam_id=jam_id,
            track_id=req.track_id,
            user_id=req.user_id,
            points=req.points,
        )
    )
    return JamQueueItemResponse.model_validate(queue_item)


@router.post("/{jam_id}/skip", response_model=ActionSuccessResponse)
def skip_jam_track(
    jam_id: int,
    req: SkipJamTrackRequest,
    use_case: Annotated[
        VoteSkipJamTrackUseCase, Depends(get_vote_skip_jam_track_use_case)
    ],
) -> ActionSuccessResponse:
    use_case.execute(
        VoteSkipJamTrackInput(
            jam_id=jam_id,
            track_id=req.track_id,
            user_id=req.user_id,
        )
    )
    return ActionSuccessResponse(success=True)


@router.post("/{jam_id}/advance", response_model=JamResponse)
def advance_jam_playback(
    jam_id: int,
    requester_user_id: Annotated[int, Query()],
    use_case: Annotated[
        AdvanceJamPlaybackUseCase, Depends(get_advance_jam_playback_use_case)
    ],
) -> JamResponse:
    jam = use_case.execute(
        jam_id=jam_id,
        requester_user_id=requester_user_id,
    )
    return JamResponse.model_validate(jam)
