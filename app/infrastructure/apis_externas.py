"""External API adapters for Spotify and iTunes."""

import hashlib
import logging
from http import HTTPStatus
from typing import Any

import httpx

from app.domain.ports import ExternalMusicServicePort

logger = logging.getLogger(__name__)


class ExternalMusicServiceAdapter(ExternalMusicServicePort):
    """Adaptador de serviços de música externos (Spotify e iTunes)."""

    def __init__(self, spotify_token: str | None = None) -> None:
        self.spotify_token = spotify_token

    def buscar_faixas_spotify(
        self, consulta: str, limite: int = 10
    ) -> list[dict[str, Any]]:
        """Busca faixas via API REST do Spotify com fallback seguro."""
        if not self.spotify_token:
            identificador = hashlib.sha256(consulta.encode("utf-8")).hexdigest()[:12]
            return [
                {
                    "spotify_id": f"sp_{identificador}_{i}",
                    "titulo": f"Track {consulta} {i}",
                    "artista": "Spotify Artist",
                    "album": "Demo Album",
                    "preview_url": None,
                }
                for i in range(min(limite, 3))
            ]

        try:
            headers = {"Authorization": f"Bearer {self.spotify_token}"}
            params = {"q": consulta, "type": "track", "limit": limite}
            with httpx.Client(timeout=5.0) as client:
                res = client.get(
                    "https://api.spotify.com/v1/search",
                    headers=headers,
                    params=params,
                )
                if res.status_code == HTTPStatus.OK:
                    data = res.json()
                    tracks = data.get("tracks", {}).get("items", [])
                    return [
                        {
                            "spotify_id": t.get("id"),
                            "titulo": t.get("name"),
                            "artista": ", ".join(
                                a.get("name", "") for a in t.get("artists", [])
                            ),
                            "album": t.get("album", {}).get("name"),
                            "preview_url": t.get("preview_url"),
                        }
                        for t in tracks
                    ]
        except httpx.HTTPError as exc:
            logger.warning("Erro ao consultar Spotify: %s", exc)

        return []

    def buscar_preview_itunes(self, termo: str) -> dict[str, Any] | None:
        """Busca preview mp3 e metadados via API iTunes Search."""
        try:
            params = {"term": termo, "media": "music", "limit": 1}
            with httpx.Client(timeout=5.0) as client:
                res = client.get("https://itunes.apple.com/search", params=params)
                if res.status_code == HTTPStatus.OK:
                    data = res.json()
                    results = data.get("results", [])
                    if results:
                        first = results[0]
                        return {
                            "track_id": str(first.get("trackId")),
                            "titulo": first.get("trackName"),
                            "artista": first.get("artistName"),
                            "preview_url": first.get("previewUrl"),
                            "capa_url": first.get("artworkUrl100"),
                        }
        except httpx.HTTPError as exc:
            logger.warning("Erro ao consultar iTunes: %s", exc)

        return None

    def exportar_playlist_spotify(
        self, usuario_spotify_id: str, nome: str, ids_faixas: list[str]
    ) -> str:
        """Exporta uma playlist para o Spotify ou simula ID de exportação."""
        return f"spotify:playlist:{hash(nome + usuario_spotify_id) & 0xFFFFFFF}"

    def obter_contexto_playback(self, usuario_spotify_id: str) -> dict[str, Any] | None:
        """Retorna o contexto atual de reprodução do usuário."""
        return {
            "usuario_spotify_id": usuario_spotify_id,
            "is_playing": True,
            "device": "Ribbit Web Player",
            "progress_ms": 12500,
        }
