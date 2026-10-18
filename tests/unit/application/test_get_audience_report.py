"""Unit tests for GetAudienceReportUseCase."""

from unittest.mock import MagicMock

from app.application.dtos.admin_dtos import AudienceReportResult
from app.application.use_cases.admin.get_audience_report import (
    GetAudienceReportUseCase,
)


def test_get_audience_report_calls_repository_counts() -> None:
    user_repo = MagicMock()
    user_repo.count_all.return_value = 42

    track_repo = MagicMock()
    track_repo.count_all.return_value = 150
    track_repo.count_active.return_value = 120

    use_case = GetAudienceReportUseCase(
        user_repo=user_repo,
        track_repo=track_repo,
    )
    result = use_case.execute()

    assert result == AudienceReportResult(
        total_users=42,
        total_tracks=150,
        active_tracks=120,
    )
    user_repo.count_all.assert_called_once()
    track_repo.count_all.assert_called_once()
    track_repo.count_active.assert_called_once()
    user_repo.list_all.assert_not_called()
    track_repo.list_active.assert_not_called()
