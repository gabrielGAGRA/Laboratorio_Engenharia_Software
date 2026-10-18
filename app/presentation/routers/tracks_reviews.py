"""Track catalog search and community reviews router."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.application.commands import (
    PublishReviewCommand,
    SearchTracksCommand,
)
from app.application.use_cases.review import (
    GetCommunityFeedUseCase,
    GetTrackReviewsUseCase,
    LikeReviewCommentUseCase,
    PublishReviewUseCase,
    SearchTracksUseCase,
)
from app.presentation.dependencies import (
    get_community_feed_use_case,
    get_like_review_comment_use_case,
    get_publish_review_use_case,
    get_search_tracks_use_case,
    get_track_reviews_use_case,
)
from app.presentation.schemas import (
    PublishReviewRequest,
    ReviewResponse,
    TrackResponse,
    TrackSearchQuery,
)

router = APIRouter(tags=["Tracks & Reviews"])


@router.get("/api/tracks/search", response_model=list[TrackResponse])
def search_tracks(
    user_id: Annotated[int, Query()],
    query: Annotated[TrackSearchQuery, Depends()],
    use_case: Annotated[SearchTracksUseCase, Depends(get_search_tracks_use_case)],
) -> list[TrackResponse]:
    tracks = use_case.execute(
        SearchTracksCommand(
            user_id=user_id,
            query=query.query,
            artist=query.artist,
            album=query.album,
            genre=query.genre,
            year=query.year,
            limit=query.limit,
            offset=query.offset,
        )
    )
    return [TrackResponse.model_validate(t) for t in tracks]


@router.post(
    "/api/reviews",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
)
def publish_review(
    req: PublishReviewRequest,
    use_case: Annotated[PublishReviewUseCase, Depends(get_publish_review_use_case)],
) -> ReviewResponse:
    review = use_case.execute(
        PublishReviewCommand(
            user_id=req.user_id,
            track_id=req.track_id,
            rating=req.rating,
            text=req.text,
        )
    )
    return ReviewResponse.model_validate(review)


@router.get("/api/reviews/feed", response_model=list[ReviewResponse])
def get_community_feed(
    use_case: Annotated[GetCommunityFeedUseCase, Depends(get_community_feed_use_case)],
) -> list[ReviewResponse]:
    reviews = use_case.execute(days=5, limit=3)
    return [ReviewResponse.model_validate(r) for r in reviews]


@router.post("/api/reviews/{review_id}/like", response_model=ReviewResponse)
def like_review(
    review_id: int,
    use_case: Annotated[
        LikeReviewCommentUseCase, Depends(get_like_review_comment_use_case)
    ],
) -> ReviewResponse:
    review = use_case.execute(review_id=review_id)
    return ReviewResponse.model_validate(review)


@router.get("/api/reviews/track/{track_id}", response_model=list[ReviewResponse])
def get_track_reviews(
    track_id: int,
    use_case: Annotated[GetTrackReviewsUseCase, Depends(get_track_reviews_use_case)],
) -> list[ReviewResponse]:
    reviews = use_case.execute(track_id=track_id)
    return [ReviewResponse.model_validate(r) for r in reviews]


__all__ = ["router"]
