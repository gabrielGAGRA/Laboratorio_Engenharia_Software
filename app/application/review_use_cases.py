"""Use cases for song reviews, community feed, and search."""

from app.domain.constants import IDADE_MINIMA_ADULTO
from app.domain.entities import AvaliacaoComentario, Musica
from app.domain.exceptions import (
    BusinessRuleViolationError,
    EntityNotFoundError,
)
from app.domain.ports import (
    AvaliacaoRepositoryPort,
    MusicaRepositoryPort,
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
    ) -> None:
        self.musica_repo = musica_repo
        self.avaliacao_repo = avaliacao_repo
        self.usuario_repo = usuario_repo

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
        if usuario.idade < IDADE_MINIMA_ADULTO:
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

    def dar_like_comentario(self, avaliacao_id: int) -> AvaliacaoComentario:
        """Incrementa a quantidade de likes de uma avaliação comunitária."""
        avaliacao = self.avaliacao_repo.buscar_por_id(avaliacao_id)
        if not avaliacao or avaliacao.is_deleted:
            raise EntityNotFoundError("Avaliação não encontrada ou excluída.")

        avaliacao.likes_count += 1
        return self.avaliacao_repo.salvar(avaliacao)

    def obter_reviews_por_musica(
        self, musica_id: int, limite: int = 50
    ) -> list[AvaliacaoComentario]:
        """Lista todas as avaliações ativas de uma faixa."""
        musica = self.musica_repo.buscar_por_id(musica_id)
        if not musica or musica.is_deleted:
            raise EntityNotFoundError("Música não encontrada ou inativa.")

        return self.avaliacao_repo.listar_por_musica(musica_id, limite=limite)
