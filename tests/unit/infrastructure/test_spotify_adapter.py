"""Unit tests for SpotifyAdapter export_playlist determinism."""

import uuid

from app.infrastructure.adapters.spotify_adapter import SpotifyAdapter


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
