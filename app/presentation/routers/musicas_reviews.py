"""Music catalog search and community reviews router."""

from fastapi import APIRouter, Depends, Query, status

from app.application.review_use_cases import ReviewUseCases
from app.presentation.dependencies import get_review_use_cases
from app.presentation.schemas import (
    MusicaResponse,
    PublicarReviewRequest,
    ReviewResponse,
)

router = APIRouter(tags=["Músicas & Reviews"])


@router.get("/api/musicas/buscar", response_model=list[MusicaResponse])
def buscar_musicas(  # noqa: PLR0913, PLR0917
    usuario_id: int = Query(...),
    termo: str | None = Query(None),
    artista: str | None = Query(None),
    album: str | None = Query(None),
    genero: str | None = Query(None),
    ano: int | None = Query(None),
    use_cases: ReviewUseCases = Depends(get_review_use_cases),
) -> list[MusicaResponse]:
    musicas = use_cases.buscar_musicas_por_filtro(
        usuario_id=usuario_id,
        termo=termo,
        artista=artista,
        album=album,
        genero=genero,
        ano=ano,
    )
    return [MusicaResponse.model_validate(m) for m in musicas]


@router.post(
    "/api/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED
)
def publicar_review(
    req: PublicarReviewRequest,
    use_cases: ReviewUseCases = Depends(get_review_use_cases),
) -> ReviewResponse:
    review = use_cases.publicar_review(
        usuario_id=req.usuario_id,
        musica_id=req.musica_id,
        nota=req.nota,
        texto=req.texto,
    )
    return ReviewResponse.model_validate(review)


@router.get("/api/reviews/feed-top5dias", response_model=list[ReviewResponse])
def feed_top5dias(
    use_cases: ReviewUseCases = Depends(get_review_use_cases),
) -> list[ReviewResponse]:
    reviews = use_cases.obter_feed_comunidade(dias=5, limite=3)
    return [ReviewResponse.model_validate(r) for r in reviews]


@router.post("/api/reviews/{review_id}/like", response_model=ReviewResponse)
def dar_like_review(
    review_id: int,
    use_cases: ReviewUseCases = Depends(get_review_use_cases),
) -> ReviewResponse:
    review = use_cases.dar_like_comentario(avaliacao_id=review_id)
    return ReviewResponse.model_validate(review)


@router.get("/api/reviews/reviews-musica", response_model=list[ReviewResponse])
def reviews_por_musica(
    musica_id: int = Query(...),
    use_cases: ReviewUseCases = Depends(get_review_use_cases),
) -> list[ReviewResponse]:
    reviews = use_cases.obter_reviews_por_musica(musica_id=musica_id)
    return [ReviewResponse.model_validate(r) for r in reviews]
