"""Unit tests for SpotifyAdapter catalog search and playlist export."""

import uuid
from http import HTTPStatus
from unittest.mock import MagicMock

import niquests
import pytest

from app.domain.exceptions import ExternalServiceError
from app.infrastructure.adapters.spotify_adapter import SpotifyAdapter


def test_spotify_search_tracks_returns_empty_list_when_no_token() -> None:
    mock_session = MagicMock(spec=niquests.Session)
    adapter = SpotifyAdapter(spotify_token=None, session=mock_session)

    results = adapter.search_tracks("Daft Punk", limit=5)

    assert results == []
    mock_session.get.assert_not_called()


def test_spotify_search_tracks_returns_catalog_tracks_on_success() -> None:
    mock_session = MagicMock(spec=niquests.Session)
    mock_response = MagicMock()
    mock_response.status_code = HTTPStatus.OK
    mock_response.json.return_value = {
        "tracks": {
            "items": [
                {
                    "id": "sp_track_1",
                    "name": "Get Lucky",
                    "artists": [{"name": "Daft Punk"}, {"name": "Pharrell Williams"}],
                    "album": {"name": "Random Access Memories"},
                    "preview_url": "https://p.scdn.co/mp3-preview/1",
                },
                {
                    "id": "sp_track_2",
                    "name": "One More Time",
                    "artists": [{"name": "Daft Punk"}],
                    "album": {"name": "Discovery"},
                    "preview_url": None,
                },
            ]
        }
    }
    mock_session.get.return_value = mock_response

    adapter = SpotifyAdapter(spotify_token="valid_token_abc", session=mock_session)
    results = adapter.search_tracks("Daft Punk", limit=2)

    assert len(results) == 2
    assert results[0].external_id == "sp_track_1"
    assert results[0].title == "Get Lucky"
    assert results[0].artist == "Daft Punk, Pharrell Williams"
    assert results[0].album == "Random Access Memories"
    assert results[0].preview_url == "https://p.scdn.co/mp3-preview/1"
    assert results[1].external_id == "sp_track_2"
    assert results[1].artist == "Daft Punk"
    assert results[1].preview_url is None

    mock_session.get.assert_called_once_with(
        "https://api.spotify.com/v1/search",
        headers={"Authorization": "Bearer valid_token_abc"},
        params={"q": "Daft Punk", "type": "track", "limit": "2"},
        timeout=5.0,
    )


def test_spotify_search_tracks_handles_empty_items() -> None:
    mock_session = MagicMock(spec=niquests.Session)
    mock_response = MagicMock()
    mock_response.status_code = HTTPStatus.OK
    mock_response.json.return_value = {"tracks": {"items": []}}
    mock_session.get.return_value = mock_response

    adapter = SpotifyAdapter(spotify_token="valid_token_abc", session=mock_session)
    results = adapter.search_tracks("Unknown Query")

    assert results == []


def test_spotify_search_tracks_raises_external_service_error_on_http_error() -> None:
    mock_session = MagicMock(spec=niquests.Session)
    mock_response = MagicMock()
    mock_response.status_code = HTTPStatus.UNAUTHORIZED
    mock_session.get.return_value = mock_response

    adapter = SpotifyAdapter(spotify_token="expired_token", session=mock_session)

    with pytest.raises(ExternalServiceError) as exc_info:
        adapter.search_tracks("Radiohead")

    assert "401" in str(exc_info.value)
    assert exc_info.value.details.get("service_name") == "Spotify"
    assert exc_info.value.details.get("status_code") == 401
    assert exc_info.value.details.get("query") == "Radiohead"


def test_spotify_search_tracks_raises_external_service_error_on_request_exception() -> (
    None
):
    mock_session = MagicMock(spec=niquests.Session)
    mock_session.get.side_effect = niquests.RequestException("DNS lookup failed")

    adapter = SpotifyAdapter(spotify_token="valid_token", session=mock_session)

    with pytest.raises(ExternalServiceError) as exc_info:
        adapter.search_tracks("Coldplay")

    assert "DNS lookup failed" in str(exc_info.value)
    assert exc_info.value.details.get("service_name") == "Spotify"
    assert exc_info.value.details.get("query") == "Coldplay"


def test_spotify_export_playlist_deterministic_uuid5() -> None:
    adapter = SpotifyAdapter()
    account_id = "user_spotify_123"
    playlist_name = "My Favorite Hits"

    expected_id = uuid.uuid5(uuid.NAMESPACE_DNS, f"{account_id}:{playlist_name}").hex[
        :22
    ]
    expected_uri = f"spotify:playlist:{expected_id}"

    uri1 = adapter.export_playlist(account_id, playlist_name, [])
    uri2 = adapter.export_playlist(account_id, playlist_name, ["track1", "track2"])

    assert uri1 == expected_uri
    assert uri2 == expected_uri
    assert uri1 == uri2


def test_spotify_export_playlist_differs_by_account_or_name() -> None:
    adapter = SpotifyAdapter()

    uri_a = adapter.export_playlist("acc1", "Rock", [])
    uri_b = adapter.export_playlist("acc2", "Rock", [])
    uri_c = adapter.export_playlist("acc1", "Pop", [])

    assert uri_a != uri_b
    assert uri_a != uri_c
    assert uri_b != uri_c
