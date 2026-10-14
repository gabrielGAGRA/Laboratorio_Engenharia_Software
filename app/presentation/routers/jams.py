"""Collaborative Jam session and queue voting router."""

from typing import Any

from fastapi import APIRouter, Depends, Query, status

from app.application.jam_use_cases import JamUseCases
from app.presentation.dependencies import get_jam_use_cases
from app.presentation.schemas import (
    CriarJamRequest,
    EntrarJamRequest,
    JamFilaResponse,
    JamResponse,
    MusicaResponse,
    PularMusicaJamRequest,
    VotarMusicaJamRequest,
)

router = APIRouter(prefix="/api/jams", tags=["Jams Colaborativas"])


@router.post("", response_model=JamResponse, status_code=status.HTTP_201_CREATED)
def criar_jam(
    req: CriarJamRequest,
    use_cases: JamUseCases = Depends(get_jam_use_cases),
) -> JamResponse:
    jam = use_cases.criar_jam(
        host_usuario_id=req.host_usuario_id,
        nome_sala=req.nome_sala,
    )
    return JamResponse.model_validate(jam)


@router.post("/entrar", response_model=JamResponse)
def entrar_jam(
    req: EntrarJamRequest,
    use_cases: JamUseCases = Depends(get_jam_use_cases),
) -> JamResponse:
    jam = use_cases.entrar_na_jam(codigo_sala=req.codigo_sala)
    return JamResponse.model_validate(jam)


@router.get("/{jam_id}/estado")
def obter_estado(
    jam_id: int,
    usuario_id: int = Query(...),
    use_cases: JamUseCases = Depends(get_jam_use_cases),
) -> dict[str, Any]:
    estado = use_cases.obter_estado_e_checar_progresso(
        jam_id=jam_id, usuario_id=usuario_id
    )
    return {
        "jam": JamResponse.model_validate(estado["jam"]),
        "musica_atual": (
            MusicaResponse.model_validate(estado["musica_atual"])
            if estado["musica_atual"]
            else None
        ),
        "fila": [JamFilaResponse.model_validate(f) for f in estado["fila"]],
    }


@router.post("/{jam_id}/votar", response_model=JamFilaResponse)
def votar_musica(
    jam_id: int,
    req: VotarMusicaJamRequest,
    use_cases: JamUseCases = Depends(get_jam_use_cases),
) -> JamFilaResponse:
    fila_item = use_cases.votar_musica_fila(
        jam_id=jam_id,
        musica_id=req.musica_id,
        usuario_id=req.usuario_id,
        pontos=req.pontos,
    )
    return JamFilaResponse.model_validate(fila_item)


@router.post("/{jam_id}/pular")
def pular_musica(
    jam_id: int,
    req: PularMusicaJamRequest,
    use_cases: JamUseCases = Depends(get_jam_use_cases),
) -> dict[str, bool]:
    use_cases.votar_musica_pular(
        jam_id=jam_id,
        musica_id=req.musica_id,
        usuario_id=req.usuario_id,
    )
    return {"sucesso": True}


@router.post("/{jam_id}/avancar", response_model=JamResponse)
def avancar_jam(
    jam_id: int,
    solicitante_usuario_id: int | None = Query(None),
    use_cases: JamUseCases = Depends(get_jam_use_cases),
) -> JamResponse:
    jam = use_cases.iniciar_ou_avancar_jam(
        jam_id=jam_id,
        solicitante_usuario_id=solicitante_usuario_id,
    )
    return JamResponse.model_validate(jam)
