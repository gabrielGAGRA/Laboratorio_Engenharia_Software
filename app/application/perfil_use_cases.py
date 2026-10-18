"""Use cases for user profile, premium features, and family plan management."""

from datetime import date
from typing import Any

from app.application.auth_use_cases import hash_password
from app.application.exceptions import (
    BusinessRuleViolationError,
    DuplicateEntityError,
    EntityNotFoundError,
    ForbiddenError,
)
from app.domain.entities import Interacao, Plano, Usuario
from app.domain.ports import (
    InteracaoRepositoryPort,
    MusicaRepositoryPort,
    PlanoRepositoryPort,
    PlaylistRepositoryPort,
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
        playlist_repo: PlaylistRepositoryPort | None = None,
    ) -> None:
        self.usuario_repo = usuario_repo
        self.plano_repo = plano_repo
        self.interacao_repo = interacao_repo
        self.musica_repo = musica_repo
        self.playlist_repo = playlist_repo

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
            "interacoes_recentes": self.interacao_repo.listar_por_usuario(usuario_id)[
                :5
            ],
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
        if usuario.titular_id is not None:
            raise ForbiddenError("Dependentes não podem alterar o plano do titular.")
        novo_plano = self.plano_repo.buscar_por_id(novo_plano_id)
        if not novo_plano:
            raise EntityNotFoundError(f"Plano com ID {novo_plano_id} não encontrado.")
        dependentes = self.usuario_repo.listar_dependentes(usuario_id)
        if dependentes and novo_plano.max_perfis < len(dependentes) + 1:
            raise BusinessRuleViolationError(
                "O novo plano não comporta os membros vinculados."
            )
        usuario.plano_id = novo_plano_id
        usuario = self.usuario_repo.salvar(usuario)
        for dependente in dependentes:
            dependente.plano_id = novo_plano_id
            self.usuario_repo.salvar(dependente)
        return usuario

    def cancelar_plano_assinatura(self, usuario_id: int) -> Usuario:
        """Cancela plano atual e reverte para o plano Free."""
        usuario = self._obter_usuario(usuario_id)
        if usuario.titular_id is not None:
            raise ForbiddenError("Dependentes não podem cancelar o plano do titular.")
        plano_free = self.plano_repo.buscar_por_nome("Free")
        if not plano_free or not plano_free.plano_id:
            raise EntityNotFoundError("Plano Free padrão não encontrado.")
        usuario.plano_id = plano_free.plano_id
        for dependente in self.usuario_repo.listar_dependentes(usuario_id):
            dependente.titular_id = None
            dependente.plano_id = plano_free.plano_id
            self.usuario_repo.salvar(dependente)
        return self.usuario_repo.salvar(usuario)

    def excluir_conta(self, usuario_id: int) -> bool:
        """Remove a conta do usuário."""
        usuario = self._obter_usuario(usuario_id)
        if usuario.titular_id is None:
            plano_free = self.plano_repo.buscar_por_nome("Free")
            if not plano_free or not plano_free.plano_id:
                raise EntityNotFoundError("Plano Free padrão não encontrado.")
            for dependente in self.usuario_repo.listar_dependentes(usuario_id):
                dependente.titular_id = None
                dependente.plano_id = plano_free.plano_id
                self.usuario_repo.salvar(dependente)
        return self.usuario_repo.excluir(usuario_id)

    # --- Recursos Exclusivos Premium ---

    def obter_frequencia_anual(self, usuario_id: int) -> dict[str, Any]:
        """Dashboard estatístico anual exclusivo para usuários Premium."""
        dados = self.obter_dashboard_premium(usuario_id)
        dados["total_curtidas"] = sum(
            item.acao in ("curtida", "amada")
            for item in self.interacao_repo.listar_por_usuario(usuario_id)
        )
        dados["horas_ouvidas_estimadas"] = round(
            dados["duracao_favoritada_segundos"] / 3600, 2
        )
        return dados

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
        categorias = {
            "like": "curtida",
            "likes": "curtida",
            "curtidas": "curtida",
            "superlike": "amada",
            "superlikes": "amada",
            "amadas": "amada",
            "rejected": "rejeitada",
            "rejeitadas": "rejeitada",
        }
        normalizada = categorias.get(categoria.strip().lower(), categoria)
        if normalizada not in ("curtida", "amada", "rejeitada"):
            raise BusinessRuleViolationError("Categoria de interação inválida.")
        return self.interacao_repo.listar_por_usuario(usuario_id, acao=normalizada)

    def editar_generos_bloqueados(
        self, usuario_id: int, novos_generos: list[str] | str
    ) -> Usuario:
        """Permite ao usuário Premium editar lista de gêneros indesejados."""
        usuario = self._obter_usuario(usuario_id)
        self._validar_premium(usuario)
        generos = (
            novos_generos.split(",")
            if isinstance(novos_generos, str)
            else novos_generos
        )
        usuario.generos_bloqueados = ",".join(
            sorted({genero.strip().lower() for genero in generos if genero.strip()})
        )
        return self.usuario_repo.salvar(usuario)

    def listar_generos_bloqueados(self, usuario_id: int) -> list[str]:
        """Retorna lista de gêneros bloqueados."""
        usuario = self._obter_usuario(usuario_id)
        self._validar_premium(usuario)
        return usuario.lista_generos_bloqueados()

    def obter_dashboard_premium(self, usuario_id: int) -> dict[str, Any]:
        """Calcula estatísticas reais do usuário Premium."""
        usuario = self._obter_usuario(usuario_id)
        self._validar_premium(usuario)
        interacoes = self.interacao_repo.listar_por_usuario(usuario_id)
        generos: dict[str, int] = {}
        duracao = 0
        if self.musica_repo:
            for interacao in interacoes:
                musica = self.musica_repo.buscar_por_id(interacao.musica_id)
                if musica and interacao.acao in ("curtida", "amada"):
                    generos[musica.genero] = generos.get(musica.genero, 0) + 1
                    duracao += musica.duracao_segundos
        playlists = (
            self.playlist_repo.listar_por_usuario(usuario_id)
            if self.playlist_repo
            else []
        )
        return {
            "usuario_id": usuario_id,
            "generos_favoritos": sorted(generos, key=generos.get, reverse=True)[:5],
            "total_playlists": len(playlists),
            "total_interacoes": len(interacoes),
            "duracao_favoritada_segundos": duracao,
        }

    # --- Gestão do Plano Família ---

    def adicionar_membro_familia(
        self,
        titular_id: int,
        email: str,
        senha: str,
        nome_exibicao: str,
        data_nascimento: date,
    ) -> Usuario:
        """Cria e vincula um dependente, inclusive menor, ao titular Família."""
        titular = self._obter_usuario(titular_id)
        plano = self._obter_plano_usuario(titular)

        if plano.max_perfis <= 1:
            raise ForbiddenError(
                "Apenas planos com suporte a múltiplos perfis podem adicionar membros."
            )

        if titular.titular_id is not None:
            raise ForbiddenError("Um dependente não pode gerenciar membros da família.")

        dependentes_atuais = self.usuario_repo.listar_dependentes(titular_id)
        if len(dependentes_atuais) + 1 >= plano.max_perfis:
            raise BusinessRuleViolationError(
                f"Limite máximo de {plano.max_perfis} perfis do plano Família atingido."
            )

        email = email.strip().lower()
        if self.usuario_repo.buscar_por_email(email):
            raise DuplicateEntityError(f"E-mail {email} já está em uso.")
        hoje = date.today()
        if data_nascimento > hoje:
            raise BusinessRuleViolationError(
                "Data de nascimento não pode estar no futuro."
            )
        idade = (
            hoje.year
            - data_nascimento.year
            - ((hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day))
        )
        dependente = Usuario(
            usuario_id=None,
            email=email,
            senha_hash=hash_password(senha),
            nome_exibicao=nome_exibicao.strip(),
            idade=idade,
            plano_id=titular.plano_id,
            titular_id=titular_id,
            data_nascimento=data_nascimento,
        )
        return self.usuario_repo.salvar(dependente)

    def remover_membro_familia(self, titular_id: int, membro_id: int) -> Usuario:
        """Desvincula dependente da família e altera seu plano para Free."""
        titular = self._obter_usuario(titular_id)
        if titular.titular_id is not None:
            raise ForbiddenError("Apenas o titular pode gerenciar a família.")
        if self._obter_plano_usuario(titular).max_perfis <= 1:
            raise ForbiddenError("O usuário não possui um plano Família.")
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
        titular = self._obter_usuario(titular_id)
        if titular.titular_id is not None:
            raise ForbiddenError("Apenas o titular pode gerenciar a família.")
        if self._obter_plano_usuario(titular).max_perfis <= 1:
            raise ForbiddenError("O usuário não possui um plano Família.")
        return self.usuario_repo.listar_dependentes(titular_id)
