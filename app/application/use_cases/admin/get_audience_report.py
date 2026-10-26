"""Use case for generating system audience and catalog metrics."""

from typing import TYPE_CHECKING

from app.application.dtos.admin_dtos import AudienceReportResponse

if TYPE_CHECKING:
    from app.application.ports.repositories.track_repository import TrackRepositoryPort
    from app.application.ports.repositories.user_repository import UserRepositoryPort


class GetAudienceReportUseCase:
    """Returns platform counters for registered users and catalog tracks."""

    def __init__(
        self,
        user_repo: UserRepositoryPort,
        track_repo: TrackRepositoryPort,
    ) -> None:
        self._user_repo = user_repo
        self._track_repo = track_repo

    def execute(self) -> AudienceReportResponse:
        total_users = len(self._user_repo.list_all())
        total_tracks = self._track_repo.count_all()
        active_tracks = len(self._track_repo.list_active(limit=1000))

        return AudienceReportResponse(
            total_users=total_users,
            total_tracks=total_tracks,
            active_tracks=active_tracks,
        )
