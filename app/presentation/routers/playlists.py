"""Playlist deck, swipe-add, and export router."""

from fastapi import APIRouter, Depends, Query, status

from app.application.playlist_use_cases import PlaylistUseCases
from app.presentation.dependencies import get_playlist_use_cases
from app.presentation.schemas import (
    DeckPlaylistRequest,
    PlaylistResponse,
    SwipeAddMusicaRequest,
)

router = APIRouter(prefix="/api/playlists", tags=["Playlists"])


@router.post(
    "/deck", response_model=PlaylistResponse, status_code=status.HTTP_201_CREATED
)
def criar_deck(
    req: DeckPlaylistRequest,
    use_cases: PlaylistUseCases = Depends(get_playlist_use_cases),
) -> PlaylistResponse:
    playlist = use_cases.criar_deck_playlist_por_parametros(
        usuario_id=req.usuario_id,
        nome=req.nome,
        duracao_minutos=req.duracao_minutos,
        genero=req.genero,
        ano=req.ano,
        artista=req.artista,
        pais=req.pais,
        descricao=req.descricao,
    )
    return PlaylistResponse.model_validate(playlist)


@router.post("/{playlist_id}/swipe-add")
def swipe_add(
    playlist_id: int,
    req: SwipeAddMusicaRequest,
    usuario_id: int = Query(...),
    use_cases: PlaylistUseCases = Depends(get_playlist_use_cases),
) -> dict[str, bool]:
    sucesso = use_cases.adicionar_musica_por_swipe(
        playlist_id=playlist_id,
        musica_id=req.musica_id,
        usuario_id=usuario_id,
    )
    return {"sucesso": sucesso}


@router.get("", response_model=list[PlaylistResponse])
def listar_biblioteca(
    usuario_id: int = Query(...),
    use_cases: PlaylistUseCases = Depends(get_playlist_use_cases),
) -> list[PlaylistResponse]:
    playlists = use_cases.listar_biblioteca_usuario(usuario_id=usuario_id)
    return [PlaylistResponse.model_validate(p) for p in playlists]


@router.post("/{playlist_id}/exportar-spotify", response_model=PlaylistResponse)
def exportar_spotify(
    playlist_id: int,
    usuario_id: int = Query(...),
    use_cases: PlaylistUseCases = Depends(get_playlist_use_cases),
) -> PlaylistResponse:
    playlist = use_cases.exportar_playlist_para_spotify(
        usuario_id=usuario_id,
        playlist_id=playlist_id,
    )
    return PlaylistResponse.model_validate(playlist)
