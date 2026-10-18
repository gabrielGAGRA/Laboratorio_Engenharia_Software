"""Domain ports and interface contracts (ABCs)."""

from abc import ABC, abstractmethod
from typing import Any

from app.domain.entities import (
    AvaliacaoComentario,
    Interacao,
    Jam,
    JamFila,
    Musica,
    Plano,
    Playlist,
    Usuario,
)


class UsuarioRepositoryPort(ABC):
    """Contrato de persistência para Usuários."""

    @abstractmethod
    def buscar_por_id(self, usuario_id: int) -> Usuario | None:
        """Busca usuário por ID."""

    @abstractmethod
    def buscar_por_email(self, email: str) -> Usuario | None:
        """Busca usuário por e-mail."""

    @abstractmethod
    def salvar(self, usuario: Usuario) -> Usuario:
        """Salva ou atualiza um usuário."""

    @abstractmethod
    def excluir(self, usuario_id: int) -> bool:
        """Remove conta de usuário."""

    @abstractmethod
    def listar_dependentes(self, titular_id: int) -> list[Usuario]:
        """Lista usuários dependentes vinculados ao titular."""

    @abstractmethod
    def listar_todos(self) -> list[Usuario]:
        """Lista todos os usuários."""


class PlanoRepositoryPort(ABC):
    """Contrato de persistência para Planos."""

    @abstractmethod
    def buscar_por_id(self, plano_id: int) -> Plano | None:
        """Busca plano por ID."""

    @abstractmethod
    def buscar_por_nome(self, nome: str) -> Plano | None:
        """Busca plano por nome."""

    @abstractmethod
    def listar_todos(self) -> list[Plano]:
        """Lista todos os planos disponíveis."""

    @abstractmethod
    def salvar(self, plano: Plano) -> Plano:
        """Salva ou atualiza um plano."""


class MusicaRepositoryPort(ABC):
    """Contrato de persistência para Músicas."""

    @abstractmethod
    def buscar_por_id(self, musica_id: int) -> Musica | None:
        """Busca música por ID."""

    @abstractmethod
    def salvar(self, musica: Musica) -> Musica:
        """Salva ou atualiza uma música."""

    @abstractmethod
    def listar_ativas(
        self,
        generos_excluidos: list[str] | None = None,
        bloquear_menores: bool = False,
        ids_excluidos: list[int] | None = None,
        limite: int | None = 50,
        cursor_id: int | None = None,
    ) -> list[Musica]:
        """Retorna músicas ativas aptas para descoberta."""

    @abstractmethod
    def buscar_por_filtros(
        self,
        artista: str | None = None,
        album: str | None = None,
        genero: str | None = None,
        ano: int | None = None,
        pais: str | None = None,
        termo: str | None = None,
        generos_excluidos: list[str] | None = None,
        bloquear_menores: bool = False,
        ids_excluidos: list[int] | None = None,
        duracao_maxima_segundos: int | None = None,
        cursor_id: int | None = None,
        limite: int | None = None,
    ) -> list[Musica]:
        """Busca músicas por filtros textuais."""

    @abstractmethod
    def contar_todas(self) -> int:
        """Retorna contagem total de faixas."""

    @abstractmethod
    def listar_bloqueadas(self) -> list[Musica]:
        """Lista faixas removidas do catálogo."""

    @abstractmethod
    def contar_ativas(self) -> int:
        """Retorna contagem de faixas visíveis no catálogo."""


class InteracaoRepositoryPort(ABC):
    """Contrato de persistência para Interações de Swipe."""

    @abstractmethod
    def buscar_por_usuario_e_musica(
        self, usuario_id: int, musica_id: int
    ) -> Interacao | None:
        """Busca interação única por usuário e música."""

    @abstractmethod
    def salvar(self, interacao: Interacao) -> Interacao:
        """Salva ou atualiza uma interação."""

    @abstractmethod
    def listar_por_usuario(
        self, usuario_id: int, acao: str | None = None
    ) -> list[Interacao]:
        """Lista interações de um usuário, opcionalmente filtradas por ação."""

    @abstractmethod
    def listar_ids_musicas_interagidas(self, usuario_id: int) -> list[int]:
        """Retorna lista de IDs de músicas já avaliadas pelo usuário."""


class PlaylistRepositoryPort(ABC):
    """Contrato de persistência para Playlists."""

    @abstractmethod
    def buscar_por_id(self, playlist_id: int) -> Playlist | None:
        """Busca playlist por ID com suas músicas."""

    @abstractmethod
    def listar_por_usuario(self, usuario_id: int) -> list[Playlist]:
        """Lista todas as playlists criadas pelo usuário."""

    @abstractmethod
    def excluir(self, playlist_id: int) -> bool:
        """Remove uma playlist e suas associações."""

    @abstractmethod
    def salvar(self, playlist: Playlist) -> Playlist:
        """Salva ou atualiza a playlist."""

    @abstractmethod
    def adicionar_musica(self, playlist_id: int, musica_id: int) -> bool:
        """Associa uma música a uma playlist."""

    @abstractmethod
    def remover_musica(self, playlist_id: int, musica_id: int) -> bool:
        """Desassocia uma música de uma playlist."""


class JamRepositoryPort(ABC):
    """Contrato de persistência para Jams colaborativas."""

    @abstractmethod
    def buscar_por_id(self, jam_id: int) -> Jam | None:
        """Busca jam por ID."""

    @abstractmethod
    def buscar_por_codigo(self, codigo_sala: str) -> Jam | None:
        """Busca jam ativa por código de sala."""

    @abstractmethod
    def salvar(self, jam: Jam) -> Jam:
        """Salva ou atualiza a jam."""

    @abstractmethod
    def adicionar_musica_fila(
        self, jam_id: int, musica_id: int, pontos: int = 0
    ) -> JamFila:
        """Adiciona música na fila da Jam."""

    @abstractmethod
    def listar_fila(self, jam_id: int) -> list[JamFila]:
        """Lista fila de reprodução ordenada por votos."""

    @abstractmethod
    def atualizar_voto_musica(
        self, jam_id: int, musica_id: int, delta_pontos: int
    ) -> JamFila | None:
        """Incrementa ou decrementa pontuação de voto de uma faixa."""

    @abstractmethod
    def remover_musica_fila(self, jam_id: int, musica_id: int) -> bool:
        """Remove música da fila."""

    @abstractmethod
    def adicionar_participante(self, jam_id: int, usuario_id: int) -> None:
        """Registra participante na sala."""

    @abstractmethod
    def eh_participante(self, jam_id: int, usuario_id: int) -> bool:
        """Informa se o usuário participa da sala."""

    @abstractmethod
    def registrar_voto_pular(self, jam_id: int, musica_id: int, usuario_id: int) -> int:
        """Registra voto único e retorna a quantidade de votos da faixa."""

    @abstractmethod
    def contar_votos_pular(self, jam_id: int, musica_id: int) -> int:
        """Conta votos únicos para pular uma faixa."""

    @abstractmethod
    def limpar_votos_pular(self, jam_id: int, musica_id: int) -> None:
        """Remove votos antigos da faixa ao avançar a sala."""


class AvaliacaoRepositoryPort(ABC):
    """Contrato de persistência para Avaliações e Comentários."""

    @abstractmethod
    def buscar_por_id(self, avaliacao_id: int) -> AvaliacaoComentario | None:
        """Busca avaliação por ID."""

    @abstractmethod
    def salvar(self, avaliacao: AvaliacaoComentario) -> AvaliacaoComentario:
        """Salva ou atualiza uma avaliação."""

    @abstractmethod
    def listar_por_musica(
        self, musica_id: int, limite: int = 50
    ) -> list[AvaliacaoComentario]:
        """Lista avaliações ativas de uma música."""

    @abstractmethod
    def listar_top_recentes(
        self, dias: int = 5, limite: int = 3
    ) -> list[AvaliacaoComentario]:
        """Retorna as avaliações mais curtidas nos últimos N dias."""

    @abstractmethod
    def buscar_por_usuario_e_musica(
        self, usuario_id: int, musica_id: int
    ) -> AvaliacaoComentario | None:
        """Busca avaliação de um usuário para uma faixa."""

    @abstractmethod
    def excluir(self, avaliacao_id: int) -> bool:
        """Remove uma avaliação."""

    @abstractmethod
    def curtir(self, avaliacao_id: int, usuario_id: int) -> AvaliacaoComentario | None:
        """Registra uma curtida única e retorna a avaliação atualizada."""


class ExternalMusicServicePort(ABC):
    """Contrato para adaptadores de serviços externos de streaming/catálogo."""

    @abstractmethod
    def buscar_faixas_spotify(
        self, consulta: str, limite: int = 10
    ) -> list[dict[str, Any]]:
        """Busca faixas via API REST do Spotify."""

    @abstractmethod
    def buscar_preview_itunes(self, termo: str) -> dict[str, Any] | None:
        """Busca preview mp3 e metadados via API iTunes Search."""

    @abstractmethod
    def exportar_playlist_spotify(
        self, usuario_spotify_id: str, nome: str, ids_faixas: list[str]
    ) -> str:
        """Exporta uma playlist para a conta do usuário no Spotify e retorna o URI/ID."""

    @abstractmethod
    def obter_contexto_playback(self, usuario_spotify_id: str) -> dict[str, Any] | None:
        """Retorna o contexto atual de reprodução do usuário."""
