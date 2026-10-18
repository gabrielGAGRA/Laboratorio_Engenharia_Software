"""Use case for generating system audience and catalog metrics."""

from dataclasses import dataclass

from app.application.dtos.admin_dtos import AudienceReportResult
lazy from app.application.ports.repositories.track_repository import TrackRepositoryPort
lazy from app.application.ports.repositories.user_repository import UserRepositoryPort


@dataclass(slots=True, frozen=True)
class GetAudienceReportUseCase:
    """Returns platform counters for registered users and catalog tracks."""

    user_repo: UserRepositoryPort
    track_repo: TrackRepositoryPort

    def execute(self) -> AudienceReportResult:
        total_users = len(self.user_repo.list_all())
        total_tracks = self.track_repo.count_all()
        active_tracks = len(self.track_repo.list_active(limit=1000))

        return AudienceReportResult(
            total_users=total_users,
            total_tracks=total_tracks,
            active_tracks=active_tracks,
        )
