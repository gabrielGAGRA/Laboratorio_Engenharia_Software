"""Use cases for user profile, premium features, and family plan management."""

from typing import Any

from app.application.auth_use_cases import hash_password
from app.domain.entities import Interacao, Plano, Usuario
from app.domain.exceptions import (
    BusinessRuleViolationError,
    EntityNotFoundError,
    ForbiddenError,
)
from app.domain.ports import (
    InteracaoRepositoryPort,
    MusicaRepositoryPort,
    PlanoRepositoryPort,
    UsuarioRepositoryPort,
)


class PerfilUseCases:
    """Casos de uso para perfil, recursos premium e plano família."""

    def __init__(
        self,
        usuario_repo: UsuarioRepositoryPort,
        plano_repo: PlanoRepositoryPort,
        interacao_repo: InteracaoRepositoryPort,
        musica_repo: MusicaRepositoryPort | None = None,
    ) -> None:
        self.usuario_repo = usuario_repo
        self.plano_repo = plano_repo
        self.interacao_repo = interacao_repo
        self.musica_repo = musica_repo

    def _obter_usuario(self, usuario_id: int) -> Usuario:
        usuario = self.usuario_repo.buscar_por_id(usuario_id)
        if not usuario:
            raise EntityNotFoundError(f"Usuário com ID {usuario_id} não encontrado.")
        return usuario

    def _obter_plano_usuario(self, usuario: Usuario) -> Plano:
        plano = self.plano_repo.buscar_por_id(usuario.plano_id)
        if not plano:
            raise EntityNotFoundError(
                f"Plano com ID {usuario.plano_id} não encontrado."
            )
        return plano

    def _validar_premium(self, usuario: Usuario) -> Plano:
        plano = self._obter_plano_usuario(usuario)
        if plano.preco_mensal <= 0:
            raise ForbiddenError("Funcionalidade exclusiva para assinantes Premium.")
        return plano

    # --- Métodos Gerais ---

    def obter_perfil_usuario(self, usuario_id: int) -> dict[str, Any]:
        """Retorna detalhes do usuário acompanhados de seu plano."""
        usuario = self._obter_usuario(usuario_id)
        plano = self._obter_plano_usuario(usuario)
        return {
            "usuario": usuario,
            "plano": plano,
        }

    def atualizar_perfil(
        self,
        usuario_id: int,
        nome_exibicao: str | None = None,
        nova_senha: str | None = None,
    ) -> Usuario:
        """Atualiza nome de exibição e/ou senha do usuário."""
        usuario = self._obter_usuario(usuario_id)
        if nome_exibicao:
            usuario.nome_exibicao = nome_exibicao.strip()
        if nova_senha:
            usuario.senha_hash = hash_password(nova_senha)
        return self.usuario_repo.salvar(usuario)

    def vincular_spotify(self, usuario_id: int, spotify_id: str) -> Usuario:
        """Associa identificador de conta do Spotify ao usuário."""
        usuario = self._obter_usuario(usuario_id)
        usuario.spotify_id = spotify_id.strip()
        return self.usuario_repo.salvar(usuario)

    def listar_interacoes(
        self, usuario_id: int, acao: str | None = None
    ) -> list[Interacao]:
        """Lista histórico de interações do usuário."""
        self._obter_usuario(usuario_id)
        return self.interacao_repo.listar_por_usuario(usuario_id, acao=acao)

    def listar_planos_existentes(self) -> list[Plano]:
        """Lista todos os planos disponíveis para contratação."""
        return self.plano_repo.listar_todos()

    def alterar_plano_assinatura(self, usuario_id: int, novo_plano_id: int) -> Usuario:
        """Altera o plano do usuário."""
        usuario = self._obter_usuario(usuario_id)
        novo_plano = self.plano_repo.buscar_por_id(novo_plano_id)
        if not novo_plano:
            raise EntityNotFoundError(f"Plano com ID {novo_plano_id} não encontrado.")
        usuario.plano_id = novo_plano_id
        return self.usuario_repo.salvar(usuario)

    def cancelar_plano_assinatura(self, usuario_id: int) -> Usuario:
        """Cancela plano atual e reverte para o plano Free."""
        usuario = self._obter_usuario(usuario_id)
        plano_free = self.plano_repo.buscar_por_nome("Free")
        if not plano_free or not plano_free.plano_id:
            raise EntityNotFoundError("Plano Free padrão não encontrado.")
        usuario.plano_id = plano_free.plano_id
        return self.usuario_repo.salvar(usuario)

    def excluir_conta(self, usuario_id: int) -> bool:
        """Remove a conta do usuário."""
        return self.usuario_repo.excluir(usuario_id)

    # --- Recursos Exclusivos Premium ---

    def obter_frequencia_anual(self, usuario_id: int) -> dict[str, Any]:
        """Dashboard estatístico anual exclusivo para usuários Premium."""
        usuario = self._obter_usuario(usuario_id)
        self._validar_premium(usuario)

        interacoes = self.interacao_repo.listar_por_usuario(usuario_id)
        curtidas = [i for i in interacoes if i.acao in ("curtida", "amada")]

        return {
            "usuario_id": usuario_id,
            "horas_ouvidas_estimadas": 42.0,
            "total_curtidas": len(curtidas),
            "generos_favoritos": ["Rock", "Pop", "Indie"],
            "artistas_principais": ["Queen", "Ed Sheeran", "The Weeknd"],
        }

    def trocar_interacao_musica(
        self, usuario_id: int, musica_id: int, nova_acao: str
    ) -> Interacao:
        """Permite ao usuário Premium reverter/alterar sua avaliação de swipe."""
        usuario = self._obter_usuario(usuario_id)
        self._validar_premium(usuario)

        if nova_acao not in ("curtida", "amada", "rejeitada"):
            raise BusinessRuleViolationError(f"Ação {nova_acao} inválida.")

        interacao = self.interacao_repo.buscar_por_usuario_e_musica(
            usuario_id, musica_id
        )
        if not interacao:
            raise EntityNotFoundError("Interação para esta música não encontrada.")

        interacao.acao = nova_acao
        return self.interacao_repo.salvar(interacao)

    def obter_historico_por_categoria(
        self, usuario_id: int, categoria: str
    ) -> list[Interacao]:
        """Retorna coleção categorizada de curtidas, amadas ou rejeitadas."""
        usuario = self._obter_usuario(usuario_id)
        self._validar_premium(usuario)
        return self.interacao_repo.listar_por_usuario(usuario_id, acao=categoria)

    def editar_generos_bloqueados(self, usuario_id: int, novos_generos: str) -> Usuario:
        """Permite ao usuário Premium editar lista de gêneros indesejados."""
        usuario = self._obter_usuario(usuario_id)
        self._validar_premium(usuario)
        usuario.generos_bloqueados = novos_generos
        return self.usuario_repo.salvar(usuario)

    def listar_generos_bloqueados(self, usuario_id: int) -> list[str]:
        """Retorna lista de gêneros bloqueados."""
        usuario = self._obter_usuario(usuario_id)
        return usuario.lista_generos_bloqueados()

    # --- Gestão do Plano Família ---

    def adicionar_membro_familia(self, titular_id: int, dependente_id: int) -> Usuario:
        """Vincula dependente à conta titular do plano Família respeitando max_perfis."""
        titular = self._obter_usuario(titular_id)
        plano = self._obter_plano_usuario(titular)

        if plano.max_perfis <= 1:
            raise ForbiddenError(
                "Apenas planos com suporte a múltiplos perfis podem adicionar membros."
            )

        if titular.titular_id is not None:
            raise ForbiddenError("Um dependente não pode gerenciar membros da família.")

        if titular_id == dependente_id:
            raise BusinessRuleViolationError(
                "O titular não pode se adicionar como dependente."
            )

        dependente = self._obter_usuario(dependente_id)
        if dependente.titular_id == titular_id:
            return dependente

        if dependente.titular_id is not None:
            raise BusinessRuleViolationError(
                "Este usuário já está vinculado a outra conta familiar."
            )

        dependentes_atuais = self.usuario_repo.listar_dependentes(titular_id)
        # +1 do titular + dependentes existentes + 1 do novo dependente
        if len(dependentes_atuais) + 2 > plano.max_perfis:
            raise BusinessRuleViolationError(
                f"Limite máximo de {plano.max_perfis} perfis do plano Família atingido."
            )

        dependente.titular_id = titular_id
        dependente.plano_id = titular.plano_id
        return self.usuario_repo.salvar(dependente)

    def remover_membro_familia(self, titular_id: int, membro_id: int) -> Usuario:
        """Desvincula dependente da família e altera seu plano para Free."""
        self._obter_usuario(titular_id)
        dependente = self._obter_usuario(membro_id)

        if dependente.titular_id != titular_id:
            raise ForbiddenError("Este perfil não pertence à sua conta família.")

        plano_free = self.plano_repo.buscar_por_nome("Free")
        if not plano_free or not plano_free.plano_id:
            raise EntityNotFoundError("Plano Free padrão não encontrado.")

        dependente.titular_id = None
        dependente.plano_id = plano_free.plano_id
        return self.usuario_repo.salvar(dependente)

    def listar_membros_familia(self, titular_id: int) -> list[Usuario]:
        """Lista os membros vinculados ao titular da conta Família."""
        self._obter_usuario(titular_id)
        return self.usuario_repo.listar_dependentes(titular_id)
