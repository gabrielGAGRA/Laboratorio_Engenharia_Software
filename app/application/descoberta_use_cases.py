"""Use cases for song discovery deck and swipe interactions."""

from app.domain.constants import IDADE_MINIMA_ADULTO
from app.domain.entities import Interacao, Musica
from app.domain.exceptions import (
    BusinessRuleViolationError,
    EntityNotFoundError,
)
from app.domain.ports import (
    InteracaoRepositoryPort,
    MusicaRepositoryPort,
    UsuarioRepositoryPort,
)

ACOES_VALIDAS = {
    "curtida": "curtida",
    "like": "curtida",
    "amada": "amada",
    "superlike": "amada",
    "rejeitada": "rejeitada",
    "rejeitar": "rejeitada",
}


class DescobertaUseCases:
    """Casos de uso para Descoberta e Swipe de faixas."""

    def __init__(
        self,
        usuario_repo: UsuarioRepositoryPort,
        musica_repo: MusicaRepositoryPort,
        interacao_repo: InteracaoRepositoryPort,
    ) -> None:
        self.usuario_repo = usuario_repo
        self.musica_repo = musica_repo
        self.interacao_repo = interacao_repo

    def obter_proxima_musica_swipe(self, usuario_id: int) -> Musica | None:
        """Retorna próxima música respeitando travas de idade, gênero e faixas já avaliadas."""
        usuario = self.usuario_repo.buscar_por_id(usuario_id)
        if not usuario:
            raise EntityNotFoundError(f"Usuário com ID {usuario_id} não encontrado.")

        bloquear_menores = usuario.idade < IDADE_MINIMA_ADULTO
        generos_bloqueados = usuario.lista_generos_bloqueados()
        ids_interagidos = self.interacao_repo.listar_ids_musicas_interagidas(usuario_id)

        candidatas = self.musica_repo.listar_ativas(
            generos_excluidos=generos_bloqueados,
            bloquear_menores=bloquear_menores,
            ids_excluidos=ids_interagidos,
            limite=1,
        )

        return candidatas[0] if candidatas else None

    def registrar_interacao_swipe(
        self, usuario_id: int, musica_id: int, acao: str
    ) -> Interacao:
        """Registra a ação gestual de swipe do usuário para a música."""
        acao_normalizada = ACOES_VALIDAS.get(acao.strip().lower())
        if not acao_normalizada:
            raise BusinessRuleViolationError(
                f"Ação inválida '{acao}'. Válidas: curtida, amada, rejeitada."
            )

        usuario = self.usuario_repo.buscar_por_id(usuario_id)
        if not usuario:
            raise EntityNotFoundError(f"Usuário com ID {usuario_id} não encontrado.")

        musica = self.musica_repo.buscar_por_id(musica_id)
        if not musica or musica.is_deleted:
            raise EntityNotFoundError(
                f"Música com ID {musica_id} não encontrada ou inativa."
            )

        interacao = Interacao(
            interacao_id=None,
            usuario_id=usuario_id,
            musica_id=musica_id,
            acao=acao_normalizada,
        )
        return self.interacao_repo.salvar(interacao)
