"""Discovery and swipe interaction router."""

from fastapi import APIRouter, Depends, Query

from app.application.descoberta_use_cases import DescobertaUseCases
from app.presentation.dependencies import get_descoberta_use_cases
from app.presentation.schemas import (
    InteracaoRequest,
    InteracaoResponse,
    MusicaResponse,
)

router = APIRouter(prefix="/api/descoberta", tags=["Descoberta"])


@router.get("/proxima", response_model=MusicaResponse | None)
def obter_proxima(
    usuario_id: int = Query(...),
    use_cases: DescobertaUseCases = Depends(get_descoberta_use_cases),
) -> MusicaResponse | None:
    musica = use_cases.obter_proxima_musica_swipe(usuario_id=usuario_id)
    if not musica:
        return None
    return MusicaResponse.model_validate(musica)


@router.post("/interagir", response_model=InteracaoResponse)
def interagir(
    req: InteracaoRequest,
    use_cases: DescobertaUseCases = Depends(get_descoberta_use_cases),
) -> InteracaoResponse:
    interacao = use_cases.registrar_interacao_swipe(
        usuario_id=req.usuario_id,
        musica_id=req.musica_id,
        acao=req.acao,
    )
    return InteracaoResponse.model_validate(interacao)
