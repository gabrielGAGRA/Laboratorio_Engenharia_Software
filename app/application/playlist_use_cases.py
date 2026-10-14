"""Use cases for playlist creation, deck generation, and export."""

from app.domain.constants import IDADE_MINIMA_ADULTO
from app.domain.entities import Playlist
from app.domain.exceptions import (
    BusinessRuleViolationError,
    EntityNotFoundError,
    ForbiddenError,
)
from app.domain.ports import (
    ExternalMusicServicePort,
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
    ) -> None:
        self.usuario_repo = usuario_repo
        self.musica_repo = musica_repo
        self.playlist_repo = playlist_repo
        self.external_service = external_service

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
        usuario = self.usuario_repo.buscar_por_id(usuario_id)
        if not usuario:
            raise EntityNotFoundError(f"Usuário com ID {usuario_id} não encontrado.")

        bloquear_menores = usuario.idade < IDADE_MINIMA_ADULTO

        candidatas = self.musica_repo.buscar_por_filtros(
            artista=artista,
            genero=genero,
            ano=ano,
        )

        if bloquear_menores:
            candidatas = [m for m in candidatas if not m.bloqueado_para_menores]

        if not candidatas:
            candidatas = self.musica_repo.listar_ativas(
                bloquear_menores=bloquear_menores,
                limite=10,
            )

        # Seleciona músicas para atingir a duração desejada (se informada)
        selecionadas = []
        segundos_alvo = (duracao_minutos * 60) if duracao_minutos else None
        segundos_acumulados = 0

        for m in candidatas:
            if segundos_alvo and segundos_acumulados + m.duracao_segundos > (
                segundos_alvo + 60
            ):
                break
            selecionadas.append(m)
            segundos_acumulados += m.duracao_segundos

        playlist = Playlist(
            playlist_id=None,
            usuario_id=usuario_id,
            nome=nome,
            descricao=descricao,
            is_exportada=False,
            musicas=selecionadas,
        )
        salva = self.playlist_repo.salvar(playlist)

        for m in selecionadas:
            if m.musica_id and salva.playlist_id:
                self.playlist_repo.adicionar_musica(salva.playlist_id, m.musica_id)

        salva.musicas = selecionadas
        return salva

    def adicionar_musica_por_swipe(
        self, playlist_id: int, musica_id: int, usuario_id: int
    ) -> bool:
        """Adiciona uma música individual à playlist via gesto de swipe com validação de dono."""
        usuario = self.usuario_repo.buscar_por_id(usuario_id)
        if not usuario:
            raise EntityNotFoundError(f"Usuário com ID {usuario_id} não encontrado.")

        playlist = self.playlist_repo.buscar_por_id(playlist_id)
        if not playlist:
            raise EntityNotFoundError(f"Playlist com ID {playlist_id} não encontrada.")

        if playlist.usuario_id != usuario_id:
            raise ForbiddenError("Acesso negado: a playlist não pertence a este usuário.")

        musica = self.musica_repo.buscar_por_id(musica_id)
        if not musica or musica.is_deleted:
            raise EntityNotFoundError(
                f"Música com ID {musica_id} não encontrada ou inativa."
            )
        if usuario.idade < IDADE_MINIMA_ADULTO and musica.bloqueado_para_menores:
            raise BusinessRuleViolationError(
                "Música bloqueada para usuários menores de idade."
            )

        return self.playlist_repo.adicionar_musica(playlist_id, musica_id)

    def listar_biblioteca_usuario(self, usuario_id: int) -> list[Playlist]:
        """Lista todas as playlists pertencentes ao usuário."""
        usuario = self.usuario_repo.buscar_por_id(usuario_id)
        if not usuario:
            raise EntityNotFoundError(f"Usuário com ID {usuario_id} não encontrado.")

        return self.playlist_repo.listar_por_usuario(usuario_id)

    def exportar_playlist_para_spotify(
        self, usuario_id: int, playlist_id: int
    ) -> Playlist:
        """Exporta a playlist para o Spotify vinculando a conta do usuário."""
        usuario = self.usuario_repo.buscar_por_id(usuario_id)
        if not usuario:
            raise EntityNotFoundError(f"Usuário com ID {usuario_id} não encontrado.")

        if not usuario.spotify_id:
            raise BusinessRuleViolationError(
                "Usuário não possui conta do Spotify vinculada."
            )

        playlist = self.playlist_repo.buscar_por_id(playlist_id)
        if not playlist:
            raise EntityNotFoundError(f"Playlist com ID {playlist_id} não encontrada.")

        if playlist.usuario_id != usuario_id:
            raise ForbiddenError("Acesso negado: você não pode exportar uma playlist que não é sua.")

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
