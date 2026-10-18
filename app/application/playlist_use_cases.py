"""Use cases for playlist creation, deck generation, and export."""

import json

from app.application.exceptions import (
    BusinessRuleViolationError,
    EntityNotFoundError,
    ForbiddenError,
)
from app.domain.entities import Interacao, Musica, Playlist, Usuario
from app.domain.ports import (
    ExternalMusicServicePort,
    InteracaoRepositoryPort,
    MusicaRepositoryPort,
    PlaylistRepositoryPort,
    UsuarioRepositoryPort,
)


class PlaylistUseCases:
    """Casos de uso para gerenciamento e montagem de playlists."""

    def __init__(
        self,
        usuario_repo: UsuarioRepositoryPort,
        musica_repo: MusicaRepositoryPort,
        playlist_repo: PlaylistRepositoryPort,
        external_service: ExternalMusicServicePort | None = None,
        interacao_repo: InteracaoRepositoryPort | None = None,
    ) -> None:
        self.usuario_repo = usuario_repo
        self.musica_repo = musica_repo
        self.playlist_repo = playlist_repo
        self.external_service = external_service
        self.interacao_repo = interacao_repo

    def _obter_usuario(self, usuario_id: int) -> Usuario:
        usuario = self.usuario_repo.buscar_por_id(usuario_id)
        if not usuario:
            raise EntityNotFoundError(f"Usuário com ID {usuario_id} não encontrado.")
        return usuario

    def criar_deck_playlist_por_parametros(  # noqa: PLR0913, PLR0917
        self,
        usuario_id: int,
        nome: str,
        duracao_minutos: int | None = None,
        genero: str | None = None,
        ano: int | None = None,
        artista: str | None = None,
        pais: str | None = None,
        descricao: str | None = None,
    ) -> Playlist:
        """Cria deck contextual de músicas ajustando pela duração e filtros especificados."""
        self._obter_usuario(usuario_id)
        duracao_maxima = duracao_minutos * 60 if duracao_minutos else None

        playlist = Playlist(
            playlist_id=None,
            usuario_id=usuario_id,
            nome=nome,
            descricao=descricao,
            is_exportada=False,
            musicas=[],
            duracao_maxima_segundos=duracao_maxima,
            filtros_deck=json.dumps(
                {
                    "genero": genero,
                    "ano": ano,
                    "artista": artista,
                    "pais": pais,
                }
            ),
        )
        return self.playlist_repo.salvar(playlist)

    def obter_deck_playlist(
        self,
        playlist_id: int,
        usuario_id: int,
        limite: int = 20,
        cursor_id: int | None = None,
    ) -> tuple[list[Musica], int | None, bool]:
        """Return a cursor page of eligible playlist suggestions."""
        usuario = self._obter_usuario(usuario_id)
        playlist = self._obter_playlist_propria(playlist_id, usuario_id)
        ids_excluidos = self._ids_musicas_rejeitadas(usuario_id)
        ids_excluidos.update(
            musica.musica_id for musica in playlist.musicas if musica.musica_id
        )
        duracao_atual = sum(musica.duracao_segundos for musica in playlist.musicas)
        restante = (
            playlist.duracao_maxima_segundos - duracao_atual
            if playlist.duracao_maxima_segundos is not None
            else None
        )
        if restante is not None and restante <= 0:
            return [], None, False
        filtros = json.loads(playlist.filtros_deck or "{}")
        musicas = self.musica_repo.buscar_por_filtros(
            **filtros,
            generos_excluidos=usuario.lista_generos_bloqueados(),
            bloquear_menores=usuario.eh_menor_de_idade(),
            ids_excluidos=list(ids_excluidos),
            duracao_maxima_segundos=restante,
            cursor_id=cursor_id,
            limite=limite + 1,
        )
        return self._pagina_de_musicas(musicas, limite)

    @staticmethod
    def _pagina_de_musicas(
        musicas: list[Musica], limite: int
    ) -> tuple[list[Musica], int | None, bool]:
        has_more = len(musicas) > limite
        items = musicas[:limite]
        next_cursor = items[-1].musica_id if has_more and items else None
        return items, next_cursor, has_more

    def _ids_musicas_rejeitadas(self, usuario_id: int) -> set[int]:
        if not self.interacao_repo:
            return set()
        return {
            interacao.musica_id
            for interacao in self.interacao_repo.listar_por_usuario(
                usuario_id, acao="rejeitada"
            )
        }

    def _obter_playlist_propria(self, playlist_id: int, usuario_id: int) -> Playlist:
        playlist = self.playlist_repo.buscar_por_id(playlist_id)
        if not playlist:
            raise EntityNotFoundError(f"Playlist com ID {playlist_id} não encontrada.")
        if playlist.usuario_id != usuario_id:
            raise ForbiddenError("A playlist não pertence a este usuário.")
        return playlist

    def adicionar_musica_por_swipe(
        self,
        playlist_id: int,
        musica_id: int,
        usuario_id: int,
        acao: str = "curtida",
    ) -> bool:
        """Adiciona uma música individual à playlist via gesto de swipe com validação de dono."""
        usuario = self._obter_usuario(usuario_id)
        playlist = self._obter_playlist_propria(playlist_id, usuario_id)

        musica = self.musica_repo.buscar_por_id(musica_id)
        if not musica or musica.is_deleted:
            raise EntityNotFoundError(
                f"Música com ID {musica_id} não encontrada ou inativa."
            )
        if usuario.eh_menor_de_idade() and musica.bloqueado_para_menores:
            raise BusinessRuleViolationError(
                "Música bloqueada para usuários menores de idade."
            )
        if musica.genero.strip().lower() in usuario.lista_generos_bloqueados():
            raise BusinessRuleViolationError("Gênero bloqueado pelo usuário.")
        duracao_atual = sum(faixa.duracao_segundos for faixa in playlist.musicas)
        if (
            playlist.duracao_maxima_segundos is not None
            and duracao_atual + musica.duracao_segundos
            > playlist.duracao_maxima_segundos
        ):
            raise BusinessRuleViolationError(
                "A música ultrapassaria a duração máxima da playlist."
            )
        if acao not in ("curtida", "amada", "like", "superlike"):
            raise BusinessRuleViolationError(
                "Apenas curtidas e superlikes podem ser adicionados à playlist."
            )
        if self.interacao_repo:
            self.interacao_repo.salvar(
                Interacao(
                    interacao_id=None,
                    usuario_id=usuario_id,
                    musica_id=musica_id,
                    acao="amada" if acao in ("amada", "superlike") else "curtida",
                )
            )
        return self.playlist_repo.adicionar_musica(playlist_id, musica_id)

    def remover_musica(self, playlist_id: int, musica_id: int, usuario_id: int) -> bool:
        """Remove uma faixa somente da playlist de propriedade do usuário."""
        self._obter_playlist_propria(playlist_id, usuario_id)
        if not self.playlist_repo.remover_musica(playlist_id, musica_id):
            raise EntityNotFoundError("Música não encontrada na playlist.")
        return True

    def excluir_playlist(self, playlist_id: int, usuario_id: int) -> bool:
        """Remove uma playlist pertencente ao usuário."""
        self._obter_playlist_propria(playlist_id, usuario_id)
        return self.playlist_repo.excluir(playlist_id)

    def listar_biblioteca_usuario(self, usuario_id: int) -> list[Playlist]:
        """Lista todas as playlists pertencentes ao usuário."""
        self._obter_usuario(usuario_id)
        return self.playlist_repo.listar_por_usuario(usuario_id)

    def obter_playlist(self, playlist_id: int, usuario_id: int) -> Playlist:
        """Obtém playlist própria com suas faixas."""
        return self._obter_playlist_propria(playlist_id, usuario_id)

    def exportar_playlist_para_spotify(
        self, usuario_id: int, playlist_id: int
    ) -> Playlist:
        """Exporta a playlist para o Spotify vinculando a conta do usuário."""
        usuario = self._obter_usuario(usuario_id)

        if not usuario.spotify_id:
            raise BusinessRuleViolationError(
                "Usuário não possui conta do Spotify vinculada."
            )

        playlist = self._obter_playlist_propria(playlist_id, usuario_id)

        if not self.external_service:
            raise BusinessRuleViolationError(
                "Serviço de integração externa indisponível."
            )

        faixas_ids = [m.spotify_id or str(m.musica_id) for m in playlist.musicas]
        sp_id = self.external_service.exportar_playlist_spotify(
            usuario.spotify_id, playlist.nome, faixas_ids
        )

        playlist.is_exportada = True
        playlist.spotify_playlist_id = sp_id
        return self.playlist_repo.salvar(playlist)
