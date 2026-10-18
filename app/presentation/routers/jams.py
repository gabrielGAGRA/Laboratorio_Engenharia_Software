"""Collaborative Jam sessions, participant voting, and queue routes."""

from fastapi import APIRouter, Depends, Query, status

from app.application.jam_use_cases import JamUseCases
from app.domain.entities import Usuario
from app.presentation.dependencies import get_current_user, get_jam_use_cases
from app.presentation.schemas import (
    CriarJamRequest,
    EntrarJamRequest,
    InteragirDeckJamRequest,
    JamEstadoResponse,
    JamFilaResponse,
    JamResponse,
    MusicaResponse,
    PaginaMusicasResponse,
    PularMusicaJamRequest,
    SalvarFaixaJamRequest,
)

router = APIRouter(prefix="/api/jams", tags=["Jams Colaborativas"])


@router.post("", response_model=JamResponse, status_code=status.HTTP_201_CREATED)
def criar_jam(
    req: CriarJamRequest,
    usuario: Usuario = Depends(get_current_user),
    use_cases: JamUseCases = Depends(get_jam_use_cases),
) -> JamResponse:
    jam = use_cases.criar_jam(
        host_usuario_id=usuario.usuario_id,
        nome_sala=req.nome_sala,
        duracao_minutos=req.duracao_minutos,
        limite_superlikes=req.limite_superlikes,
        meta_votos_pular=req.meta_votos_pular,
        fonte_deck=req.fonte_deck,
        playlist_origem_id=req.playlist_origem_id,
    )
    return JamResponse.model_validate(jam)


@router.post("/entrar", response_model=JamResponse)
def entrar_jam(
    req: EntrarJamRequest,
    usuario: Usuario = Depends(get_current_user),
    use_cases: JamUseCases = Depends(get_jam_use_cases),
) -> JamResponse:
    jam = use_cases.entrar_na_jam(req.codigo_sala, usuario.usuario_id)
    return JamResponse.model_validate(jam)


@router.get("/{jam_id}/estado", response_model=JamEstadoResponse)
def obter_estado(
    jam_id: int,
    usuario: Usuario = Depends(get_current_user),
    use_cases: JamUseCases = Depends(get_jam_use_cases),
) -> JamEstadoResponse:
    estado = use_cases.obter_estado_e_checar_progresso(jam_id, usuario.usuario_id)
    return JamEstadoResponse(
        jam=JamResponse.model_validate(estado["jam"]),
        musica_atual=(
            MusicaResponse.model_validate(estado["musica_atual"])
            if estado["musica_atual"]
            else None
        ),
        fila=[JamFilaResponse.model_validate(item) for item in estado["fila"]],
        votos_pular=estado["votos_pular"],
    )


@router.post("/{jam_id}/votar-pular")
def votar_pular(
    jam_id: int,
    req: PularMusicaJamRequest,
    usuario: Usuario = Depends(get_current_user),
    use_cases: JamUseCases = Depends(get_jam_use_cases),
) -> dict[str, object]:
    return use_cases.votar_musica_pular(jam_id, usuario.usuario_id, req.musica_id)


@router.post("/{jam_id}/curtir-fila")
def curtir_fila(
    jam_id: int,
    req: SalvarFaixaJamRequest,
    usuario: Usuario = Depends(get_current_user),
    use_cases: JamUseCases = Depends(get_jam_use_cases),
) -> dict[str, bool]:
    return {
        "sucesso": use_cases.salvar_faixa_fila(
            jam_id, usuario.usuario_id, req.musica_id, req.playlist_id
        )
    }


@router.get("/{jam_id}/deck-adicionar", response_model=PaginaMusicasResponse)
def obter_deck_adicionar(
    jam_id: int,
    limite: int = Query(default=20, ge=1, le=100),
    cursor_id: int | None = Query(default=None, gt=0),
    usuario: Usuario = Depends(get_current_user),
    use_cases: JamUseCases = Depends(get_jam_use_cases),
) -> PaginaMusicasResponse:
    musicas, next_cursor, has_more = use_cases.obter_deck_adicionar(
        jam_id, usuario.usuario_id, limite, cursor_id
    )
    return PaginaMusicasResponse(
        items=[MusicaResponse.model_validate(musica) for musica in musicas],
        next_cursor=next_cursor,
        has_more=has_more,
    )


@router.post("/{jam_id}/interagir-deck", response_model=JamFilaResponse)
def interagir_deck(
    jam_id: int,
    req: InteragirDeckJamRequest,
    usuario: Usuario = Depends(get_current_user),
    use_cases: JamUseCases = Depends(get_jam_use_cases),
) -> JamFilaResponse:
    item = use_cases.interagir_deck(jam_id, req.musica_id, usuario.usuario_id, req.acao)
    return JamFilaResponse.model_validate(item)


@router.post("/{jam_id}/encerrar", response_model=JamResponse)
def encerrar_jam(
    jam_id: int,
    usuario: Usuario = Depends(get_current_user),
    use_cases: JamUseCases = Depends(get_jam_use_cases),
) -> JamResponse:
    jam = use_cases.encerrar_jam(jam_id, usuario.usuario_id)
    return JamResponse.model_validate(jam)
