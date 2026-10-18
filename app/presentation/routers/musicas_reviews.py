"""Catalog search, favorites, and community review routes."""

from typing import Any

from fastapi import APIRouter, Depends, status

from app.application.exceptions import EntityNotFoundError
from app.application.review_use_cases import ReviewUseCases
from app.domain.entities import Usuario
from app.presentation.dependencies import get_current_user, get_review_use_cases
from app.presentation.schemas import (
    MusicaResponse,
    MusicaReviewsResponse,
    PublicarReviewRequest,
    ReviewResponse,
    SalvarMusicaRequest,
)

router = APIRouter(tags=["Músicas & Reviews"])


@router.get("/api/musicas/buscar", response_model=list[MusicaResponse])
def buscar_musicas(
    termo: str | None = None,
    artista: str | None = None,
    album: str | None = None,
    genero: str | None = None,
    ano: int | None = None,
    usuario: Usuario = Depends(get_current_user),
    use_cases: ReviewUseCases = Depends(get_review_use_cases),
) -> list[MusicaResponse]:
    musicas = use_cases.buscar_musicas_por_filtro(
        usuario_id=usuario.usuario_id,
        termo=termo,
        artista=artista,
        album=album,
        genero=genero,
        ano=ano,
    )
    return [MusicaResponse.model_validate(musica) for musica in musicas]


@router.post(
    "/api/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED
)
def publicar_review(
    req: PublicarReviewRequest,
    usuario: Usuario = Depends(get_current_user),
    use_cases: ReviewUseCases = Depends(get_review_use_cases),
) -> ReviewResponse:
    review = use_cases.publicar_review(
        usuario_id=usuario.usuario_id,
        musica_id=req.musica_id,
        nota=req.nota,
        texto=req.texto,
    )
    return ReviewResponse.model_validate(review)


@router.get("/api/reviews/ultimas-interagidas")
def ultimas_interagidas(
    usuario: Usuario = Depends(get_current_user),
    use_cases: ReviewUseCases = Depends(get_review_use_cases),
) -> list[dict[str, Any]]:
    return [
        {
            "interacao": item["interacao"],
            "musica": MusicaResponse.model_validate(item["musica"]),
        }
        for item in use_cases.obter_ultimas_interagidas(usuario.usuario_id)
    ]


@router.get("/api/reviews/feed-top5dias", response_model=list[ReviewResponse])
def feed_top5dias(
    use_cases: ReviewUseCases = Depends(get_review_use_cases),
) -> list[ReviewResponse]:
    reviews = use_cases.obter_feed_comunidade(dias=14, limite=5)
    return [ReviewResponse.model_validate(review) for review in reviews]


@router.post("/api/reviews/{review_id}/like", response_model=ReviewResponse)
def dar_like_review(
    review_id: int,
    usuario: Usuario = Depends(get_current_user),
    use_cases: ReviewUseCases = Depends(get_review_use_cases),
) -> ReviewResponse:
    review = use_cases.dar_like_comentario(review_id, usuario.usuario_id)
    return ReviewResponse.model_validate(review)


@router.post("/api/reviews/{musica_id}/curtir-busca")
def curtir_musica_busca(
    musica_id: int,
    req: SalvarMusicaRequest,
    usuario: Usuario = Depends(get_current_user),
    use_cases: ReviewUseCases = Depends(get_review_use_cases),
) -> dict[str, bool]:
    return {
        "sucesso": use_cases.salvar_musica_curti_busca(
            usuario.usuario_id, musica_id, req.playlist_id
        )
    }


@router.get("/api/reviews/musica/{musica_id}", response_model=MusicaReviewsResponse)
def reviews_por_musica(
    musica_id: int,
    use_cases: ReviewUseCases = Depends(get_review_use_cases),
) -> MusicaReviewsResponse:
    musica = use_cases.musica_repo.buscar_por_id(musica_id)
    if not musica or musica.is_deleted:
        raise EntityNotFoundError("Música não encontrada ou inativa.")
    reviews = use_cases.obter_reviews_por_musica(musica_id)
    return MusicaReviewsResponse(
        musica=MusicaResponse.model_validate(musica),
        reviews=[ReviewResponse.model_validate(review) for review in reviews],
    )


@router.delete("/api/reviews/{review_id}")
def excluir_review(
    review_id: int,
    usuario: Usuario = Depends(get_current_user),
    use_cases: ReviewUseCases = Depends(get_review_use_cases),
) -> dict[str, bool]:
    return {"sucesso": use_cases.excluir_review(review_id, usuario.usuario_id)}
