"""Playlist library, deck, and export routes."""

from fastapi import APIRouter, Depends, Query, status

from app.application.playlist_use_cases import PlaylistUseCases
from app.domain.entities import Playlist, Usuario
from app.presentation.dependencies import get_current_user, get_playlist_use_cases
from app.presentation.schemas import (
    DeckPlaylistRequest,
    MusicaResponse,
    PaginaMusicasResponse,
    PlaylistResponse,
    SwipeAddMusicaRequest,
)

router = APIRouter(prefix="/api/playlists", tags=["Playlists"])


def _resposta_playlist(playlist: Playlist) -> PlaylistResponse:
    resposta = PlaylistResponse.model_validate(playlist)
    resposta.duracao_total_segundos = sum(
        musica.duracao_segundos for musica in resposta.musicas
    )
    return resposta


@router.post(
    "/deck", response_model=PlaylistResponse, status_code=status.HTTP_201_CREATED
)
def criar_deck(
    req: DeckPlaylistRequest,
    usuario: Usuario = Depends(get_current_user),
    use_cases: PlaylistUseCases = Depends(get_playlist_use_cases),
) -> PlaylistResponse:
    playlist = use_cases.criar_deck_playlist_por_parametros(
        usuario_id=usuario.usuario_id,
        nome=req.nome,
        duracao_minutos=req.duracao_minutos,
        genero=req.genero,
        ano=req.ano,
        artista=req.artista,
        pais=req.pais,
        descricao=req.descricao,
    )
    return _resposta_playlist(playlist)


@router.get("", response_model=list[PlaylistResponse])
def listar_biblioteca(
    usuario: Usuario = Depends(get_current_user),
    use_cases: PlaylistUseCases = Depends(get_playlist_use_cases),
) -> list[PlaylistResponse]:
    playlists = use_cases.listar_biblioteca_usuario(usuario_id=usuario.usuario_id)
    resposta: list[PlaylistResponse] = []
    for playlist in playlists:
        if playlist.playlist_id is None:
            raise RuntimeError("Playlist persistida sem identificador.")
        resposta.append(
            _resposta_playlist(
                use_cases.obter_playlist(playlist.playlist_id, usuario.usuario_id)
            )
        )
    return resposta


@router.get("/{playlist_id}/deck", response_model=PaginaMusicasResponse)
def obter_deck(
    playlist_id: int,
    limite: int = Query(default=20, ge=1, le=100),
    cursor_id: int | None = Query(default=None, gt=0),
    usuario: Usuario = Depends(get_current_user),
    use_cases: PlaylistUseCases = Depends(get_playlist_use_cases),
) -> PaginaMusicasResponse:
    musicas, next_cursor, has_more = use_cases.obter_deck_playlist(
        playlist_id, usuario.usuario_id, limite, cursor_id
    )
    return PaginaMusicasResponse(
        items=[MusicaResponse.model_validate(musica) for musica in musicas],
        next_cursor=next_cursor,
        has_more=has_more,
    )


@router.post("/{playlist_id}/swipe-add")
def swipe_add(
    playlist_id: int,
    req: SwipeAddMusicaRequest,
    usuario: Usuario = Depends(get_current_user),
    use_cases: PlaylistUseCases = Depends(get_playlist_use_cases),
) -> dict[str, bool]:
    sucesso = use_cases.adicionar_musica_por_swipe(
        playlist_id=playlist_id,
        musica_id=req.musica_id,
        usuario_id=usuario.usuario_id,
        acao=req.acao,
    )
    return {"sucesso": sucesso}


@router.get("/{playlist_id}", response_model=PlaylistResponse)
def obter_playlist(
    playlist_id: int,
    usuario: Usuario = Depends(get_current_user),
    use_cases: PlaylistUseCases = Depends(get_playlist_use_cases),
) -> PlaylistResponse:
    return _resposta_playlist(use_cases.obter_playlist(playlist_id, usuario.usuario_id))


@router.delete("/{playlist_id}")
def excluir_playlist(
    playlist_id: int,
    usuario: Usuario = Depends(get_current_user),
    use_cases: PlaylistUseCases = Depends(get_playlist_use_cases),
) -> dict[str, bool]:
    return {"sucesso": use_cases.excluir_playlist(playlist_id, usuario.usuario_id)}


@router.delete("/{playlist_id}/musicas/{musica_id}")
def remover_musica(
    playlist_id: int,
    musica_id: int,
    usuario: Usuario = Depends(get_current_user),
    use_cases: PlaylistUseCases = Depends(get_playlist_use_cases),
) -> dict[str, bool]:
    return {
        "sucesso": use_cases.remover_musica(playlist_id, musica_id, usuario.usuario_id)
    }


@router.post("/{playlist_id}/exportar-spotify", response_model=PlaylistResponse)
def exportar_spotify(
    playlist_id: int,
    usuario: Usuario = Depends(get_current_user),
    use_cases: PlaylistUseCases = Depends(get_playlist_use_cases),
) -> PlaylistResponse:
    playlist = use_cases.exportar_playlist_para_spotify(
        usuario_id=usuario.usuario_id,
        playlist_id=playlist_id,
    )
    return _resposta_playlist(playlist)
