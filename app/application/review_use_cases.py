"""Use cases for song reviews, community feed, and search."""

from app.application.exceptions import (
    BusinessRuleViolationError,
    DuplicateEntityError,
    EntityNotFoundError,
    ForbiddenError,
)
from app.domain.entities import AvaliacaoComentario, Interacao, Musica
from app.domain.ports import (
    AvaliacaoRepositoryPort,
    ExternalMusicServicePort,
    InteracaoRepositoryPort,
    MusicaRepositoryPort,
    PlaylistRepositoryPort,
    UsuarioRepositoryPort,
)

NOTA_MINIMA = 1
NOTA_MAXIMA = 5


class ReviewUseCases:
    """Casos de uso para busca de músicas e avaliações comunitárias."""

    def __init__(
        self,
        musica_repo: MusicaRepositoryPort,
        avaliacao_repo: AvaliacaoRepositoryPort,
        usuario_repo: UsuarioRepositoryPort,
        interacao_repo: InteracaoRepositoryPort,
        playlist_repo: PlaylistRepositoryPort,
        external_service: ExternalMusicServicePort,
    ) -> None:
        self.musica_repo = musica_repo
        self.avaliacao_repo = avaliacao_repo
        self.usuario_repo = usuario_repo
        self.interacao_repo = interacao_repo
        self.playlist_repo = playlist_repo
        self.external_service = external_service

    def buscar_musicas_por_filtro(  # noqa: PLR0913, PLR0917
        self,
        usuario_id: int,
        artista: str | None = None,
        album: str | None = None,
        genero: str | None = None,
        ano: int | None = None,
        termo: str | None = None,
    ) -> list[Musica]:
        """Busca catálogo por artista, álbum, gênero, ano ou termo geral."""
        usuario = self.usuario_repo.buscar_por_id(usuario_id)
        if not usuario:
            raise EntityNotFoundError(f"Usuário com ID {usuario_id} não encontrado.")

        musicas = self.musica_repo.buscar_por_filtros(
            artista=artista,
            album=album,
            genero=genero,
            ano=ano,
            termo=termo,
        )
        consulta = termo or artista or album or genero or (str(ano) if ano else None)
        if not musicas and consulta:
            for faixa in self.external_service.buscar_faixas_spotify(consulta):
                musica = Musica(
                    musica_id=None,
                    titulo=str(faixa.get("titulo") or consulta),
                    artista=str(faixa.get("artista") or "Artista desconhecido"),
                    album=faixa.get("album"),
                    duracao_segundos=int(faixa.get("duracao_segundos") or 180),
                    genero=str(faixa.get("genero") or "Desconhecido"),
                    spotify_id=faixa.get("spotify_id"),
                )
                musicas.append(self.musica_repo.salvar(musica))
        if usuario.eh_menor_de_idade():
            musicas = [
                musica for musica in musicas if not musica.bloqueado_para_menores
            ]
        return musicas

    def publicar_review(
        self, usuario_id: int, musica_id: int, nota: int, texto: str | None = None
    ) -> AvaliacaoComentario:
        """Publica avaliação e comentário para uma faixa musical."""
        if not (NOTA_MINIMA <= nota <= NOTA_MAXIMA):
            raise BusinessRuleViolationError(
                f"A nota da avaliação deve estar entre {NOTA_MINIMA} e {NOTA_MAXIMA}."
            )

        usuario = self.usuario_repo.buscar_por_id(usuario_id)
        if not usuario:
            raise EntityNotFoundError(f"Usuário com ID {usuario_id} não encontrado.")

        musica = self.musica_repo.buscar_por_id(musica_id)
        if not musica or musica.is_deleted:
            raise EntityNotFoundError(
                f"Música com ID {musica_id} não encontrada ou inativa."
            )
        if self.avaliacao_repo.buscar_por_usuario_e_musica(usuario_id, musica_id):
            raise DuplicateEntityError("Você já avaliou esta música.")

        avaliacao = AvaliacaoComentario(
            avaliacao_id=None,
            usuario_id=usuario_id,
            musica_id=musica_id,
            nota=nota,
            texto=texto.strip() if texto else None,
            likes_count=0,
            is_deleted=False,
        )
        return self.avaliacao_repo.salvar(avaliacao)

    def obter_feed_comunidade(
        self, dias: int = 5, limite: int = 3
    ) -> list[AvaliacaoComentario]:
        """Retorna o feed com os top 3 comentários com mais curtidas nos últimos 5 dias."""
        return self.avaliacao_repo.listar_top_recentes(dias=dias, limite=limite)

    def dar_like_comentario(
        self, avaliacao_id: int, usuario_id: int
    ) -> AvaliacaoComentario:
        """Incrementa a quantidade de likes de uma avaliação comunitária."""
        if not self.usuario_repo.buscar_por_id(usuario_id):
            raise EntityNotFoundError(f"Usuário com ID {usuario_id} não encontrado.")
        avaliacao = self.avaliacao_repo.buscar_por_id(avaliacao_id)
        if not avaliacao or avaliacao.is_deleted:
            raise EntityNotFoundError("Avaliação não encontrada ou excluída.")
        atualizada = self.avaliacao_repo.curtir(avaliacao_id, usuario_id)
        if not atualizada:
            raise EntityNotFoundError("Avaliação não encontrada ou excluída.")
        return atualizada

    def excluir_review(self, avaliacao_id: int, usuario_id: int) -> bool:
        """Exclui uma avaliação somente pelo seu autor."""
        avaliacao = self.avaliacao_repo.buscar_por_id(avaliacao_id)
        if not avaliacao:
            raise EntityNotFoundError("Avaliação não encontrada.")
        if avaliacao.usuario_id != usuario_id:
            raise ForbiddenError("Somente o autor pode excluir esta avaliação.")
        return self.avaliacao_repo.excluir(avaliacao_id)

    def obter_ultimas_interagidas(self, usuario_id: int) -> list[dict[str, object]]:
        """Retorna faixas da atividade recente do usuário."""
        if not self.usuario_repo.buscar_por_id(usuario_id):
            raise EntityNotFoundError(f"Usuário com ID {usuario_id} não encontrado.")
        resultado: list[dict[str, object]] = []
        for interacao in self.interacao_repo.listar_por_usuario(usuario_id)[:20]:
            musica = self.musica_repo.buscar_por_id(interacao.musica_id)
            if musica and not musica.is_deleted:
                resultado.append({"interacao": interacao, "musica": musica})
        return resultado

    def salvar_musica_curti_busca(
        self, usuario_id: int, musica_id: int, playlist_id: int | None = None
    ) -> bool:
        """Salva uma faixa nas curtidas e opcionalmente em playlist própria."""
        usuario = self.usuario_repo.buscar_por_id(usuario_id)
        if not usuario:
            raise EntityNotFoundError(f"Usuário com ID {usuario_id} não encontrado.")
        musica = self.musica_repo.buscar_por_id(musica_id)
        if not musica or musica.is_deleted:
            raise EntityNotFoundError("Música não encontrada ou inativa.")
        if usuario.eh_menor_de_idade() and musica.bloqueado_para_menores:
            raise BusinessRuleViolationError(
                "Música bloqueada para usuários menores de idade."
            )
        if playlist_id is not None:
            playlist = self.playlist_repo.buscar_por_id(playlist_id)
            if not playlist:
                raise EntityNotFoundError("Playlist não encontrada.")
            if playlist.usuario_id != usuario_id:
                raise ForbiddenError("A playlist não pertence a este usuário.")
        self.interacao_repo.salvar(
            Interacao(
                interacao_id=None,
                usuario_id=usuario_id,
                musica_id=musica_id,
                acao="amada",
            )
        )
        if playlist_id is not None:
            self.playlist_repo.adicionar_musica(playlist_id, musica_id)
        return True

    def obter_reviews_por_musica(
        self, musica_id: int, limite: int = 50
    ) -> list[AvaliacaoComentario]:
        """Lista todas as avaliações ativas de uma faixa."""
        musica = self.musica_repo.buscar_por_id(musica_id)
        if not musica or musica.is_deleted:
            raise EntityNotFoundError("Música não encontrada ou inativa.")

        return self.avaliacao_repo.listar_por_musica(musica_id, limite=limite)
