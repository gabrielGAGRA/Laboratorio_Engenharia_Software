"""Playlist deck, swipe-add, and export router."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.application.commands import (
    AddTrackToPlaylistCommand,
    CreateDeckPlaylistCommand,
)
from app.application.use_cases.playlist import (
    AddTrackToPlaylistUseCase,
    CreateDeckPlaylistUseCase,
    ExportPlaylistToSpotifyUseCase,
    ListUserPlaylistsUseCase,
)
from app.presentation.dependencies import (
    get_add_track_to_playlist_use_case,
    get_create_deck_playlist_use_case,
    get_export_playlist_to_spotify_use_case,
    get_list_user_playlists_use_case,
)
from app.presentation.schemas import (
    ActionSuccessResponse,
    DeckPlaylistRequest,
    PlaylistResponse,
    SwipeAddTrackRequest,
)

router = APIRouter(prefix="/api/playlists", tags=["Playlists"])


@router.post(
    "/deck", response_model=PlaylistResponse, status_code=status.HTTP_201_CREATED
)
def create_deck_playlist(
    req: DeckPlaylistRequest,
    use_case: Annotated[
        CreateDeckPlaylistUseCase, Depends(get_create_deck_playlist_use_case)
    ],
) -> PlaylistResponse:
    playlist = use_case.execute(
        CreateDeckPlaylistCommand(
            user_id=req.user_id,
            name=req.name,
            duration_minutes=req.duration_minutes,
            genre=req.genre,
            year=req.year,
            artist=req.artist,
            country=req.country,
            description=req.description,
        )
    )
    return PlaylistResponse.model_validate(playlist)


@router.post("/{playlist_id}/swipe-add", response_model=ActionSuccessResponse)
def swipe_add_track(
    playlist_id: int,
    req: SwipeAddTrackRequest,
    user_id: Annotated[int, Query()],
    use_case: Annotated[
        AddTrackToPlaylistUseCase, Depends(get_add_track_to_playlist_use_case)
    ],
) -> ActionSuccessResponse:
    use_case.execute(
        AddTrackToPlaylistCommand(
            playlist_id=playlist_id,
            track_id=req.track_id,
            user_id=user_id,
        )
    )
    return ActionSuccessResponse(success=True)


@router.get("", response_model=list[PlaylistResponse])
def list_playlists(
    user_id: Annotated[int, Query()],
    use_case: Annotated[
        ListUserPlaylistsUseCase, Depends(get_list_user_playlists_use_case)
    ],
) -> list[PlaylistResponse]:
    playlists = use_case.execute(user_id=user_id)
    return [PlaylistResponse.model_validate(p) for p in playlists]


@router.post("/{playlist_id}/export-spotify", response_model=PlaylistResponse)
def export_playlist_to_spotify(
    playlist_id: int,
    user_id: Annotated[int, Query()],
    use_case: Annotated[
        ExportPlaylistToSpotifyUseCase,
        Depends(get_export_playlist_to_spotify_use_case),
    ],
) -> PlaylistResponse:
    playlist = use_case.execute(
        user_id=user_id,
        playlist_id=playlist_id,
    )
    return PlaylistResponse.model_validate(playlist)


__all__ = ["router"]
