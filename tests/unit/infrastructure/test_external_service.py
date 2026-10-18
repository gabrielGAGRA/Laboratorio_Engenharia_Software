"""Unit tests for ExternalMusicServiceAdapter exception translation."""

from unittest.mock import patch

import niquests
import pytest

from app.domain.exceptions import ExternalServiceError
from app.infrastructure.adapters.itunes_adapter import ITunesAdapter


def test_find_preview_raises_external_service_error_on_network_failure() -> None:
    adapter = ITunesAdapter()

    with (
        patch(
            "niquests.Session.get",
            side_effect=niquests.RequestException("Connection timed out"),
        ),
        pytest.raises(ExternalServiceError) as exc_info,
    ):
        adapter.find_preview("Bohemian Rhapsody")

    assert "Connection timed out" in str(exc_info.value)
    assert exc_info.value.details.get("service_name") == "iTunes"
