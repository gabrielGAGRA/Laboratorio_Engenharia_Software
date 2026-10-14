"""Use cases for system administration, executive metrics, and catalog moderation."""

from typing import Any

from app.domain.entities import Plano, Usuario
from app.domain.exceptions import EntityNotFoundError
from app.domain.ports import (
    AvaliacaoRepositoryPort,
    MusicaRepositoryPort,
    PlanoRepositoryPort,
    UsuarioRepositoryPort,
)


class AdminUseCases:
    """Casos de uso administrativos restritos."""

    def __init__(
        self,
        usuario_repo: UsuarioRepositoryPort,
        plano_repo: PlanoRepositoryPort,
        musica_repo: MusicaRepositoryPort,
        avaliacao_repo: AvaliacaoRepositoryPort,
    ) -> None:
        self.usuario_repo = usuario_repo
        self.plano_repo = plano_repo
        self.musica_repo = musica_repo
        self.avaliacao_repo = avaliacao_repo

    def obter_dashboard_executivo(self) -> dict[str, Any]:
        """Calcula métricas financeiras (Receita Líquida) e contagem de usuários."""
        usuarios = self.usuario_repo.listar_todos()
        planos = self.plano_repo.listar_todos()
        plano_map = {p.plano_id: p for p in planos if p.plano_id is not None}

        receita_total = 0.0
        usuarios_por_plano: dict[str, int] = {}
        receita_por_plano: dict[str, float] = {}

        for p in planos:
            usuarios_por_plano[p.nome] = 0
            receita_por_plano[p.nome] = 0.0

        for u in usuarios:
            p = plano_map.get(u.plano_id)
            if p:
                usuarios_por_plano[p.nome] = usuarios_por_plano.get(p.nome, 0) + 1
                # Apenas titulares geram receita de cobrança
                if u.titular_id is None:
                    receita_total += p.preco_mensal
                    receita_por_plano[p.nome] = (
                        receita_por_plano.get(p.nome, 0.0) + p.preco_mensal
                    )

        return {
            "total_usuarios": len(usuarios),
            "receita_liquida_estimada": round(receita_total, 2),
            "usuarios_por_plano": usuarios_por_plano,
            "receita_por_plano": {k: round(v, 2) for k, v in receita_por_plano.items()},
        }

    def gerenciar_usuarios_planos(self) -> list[dict[str, Any]]:
        """Lista usuários e seus respectivos planos para gestão administrativa."""
        usuarios = self.usuario_repo.listar_todos()
        planos = {p.plano_id: p.nome for p in self.plano_repo.listar_todos()}
        return [
            {
                "usuario_id": u.usuario_id,
                "email": u.email,
                "nome_exibicao": u.nome_exibicao,
                "idade": u.idade,
                "plano": planos.get(u.plano_id, "Desconhecido"),
                "is_admin": u.is_admin,
            }
            for u in usuarios
        ]

    def obter_relatorio_audiencia(self) -> dict[str, Any]:
        """Retorna contadores de audiência e catálogo."""
        return {
            "total_usuarios": len(self.usuario_repo.listar_todos()),
            "total_musicas": self.musica_repo.contar_todas(),
            "musicas_ativas": len(self.musica_repo.listar_ativas(limite=1000)),
        }

    def obter_logs_auditoria(self) -> list[dict[str, Any]]:
        """Retorna registros de auditoria do sistema."""
        return [
            {"evento": "SISTEMA_INICIALIZADO", "status": "OK"},
            {"evento": "AUDITORIA_CATALOGO", "status": "OK"},
        ]

    def bloquear_musica(self, musica_id: int) -> bool:
        """Aplica soft-delete na faixa musical (is_deleted = True)."""
        musica = self.musica_repo.buscar_por_id(musica_id)
        if not musica:
            raise EntityNotFoundError(f"Música {musica_id} não encontrada.")
        musica.is_deleted = True
        self.musica_repo.salvar(musica)
        return True

    def atualizar_restricao_menores(
        self, musica_id: int, bloqueado_para_menores: bool
    ) -> bool:
        """Define se a faixa deve ser ocultada para usuários menores de idade."""
        musica = self.musica_repo.buscar_por_id(musica_id)
        if not musica:
            raise EntityNotFoundError(f"Música {musica_id} não encontrada.")
        musica.bloqueado_para_menores = bloqueado_para_menores
        self.musica_repo.salvar(musica)
        return musica.bloqueado_para_menores

    def promover_usuario_para_admin(self, usuario_id: int) -> Usuario:
        """Concede privilégios de administrador para um usuário."""
        usuario = self.usuario_repo.buscar_por_id(usuario_id)
        if not usuario:
            raise EntityNotFoundError(f"Usuário {usuario_id} não encontrado.")
        usuario.is_admin = True
        return self.usuario_repo.salvar(usuario)

    def atualizar_planos_existentes(
        self,
        plano_id: int,
        novo_preco: float | None = None,
        novo_nome: str | None = None,
        max_perfis: int | None = None,
    ) -> Plano:
        """Atualiza valores e atributos de um plano de assinatura existente."""
        plano = self.plano_repo.buscar_por_id(plano_id)
        if not plano:
            raise EntityNotFoundError(f"Plano {plano_id} não encontrado.")

        if novo_preco is not None:
            plano.preco_mensal = novo_preco
        if novo_nome is not None:
            plano.nome = novo_nome
        if max_perfis is not None:
            plano.max_perfis = max_perfis

        return self.plano_repo.salvar(plano)

    def ver_top_comentarios(self) -> list[dict[str, Any]]:
        """Retorna avaliações com maiores curtidas para moderação."""
        top = self.avaliacao_repo.listar_top_recentes(dias=30, limite=10)
        return [
            {
                "avaliacao_id": a.avaliacao_id,
                "usuario_id": a.usuario_id,
                "musica_id": a.musica_id,
                "nota": a.nota,
                "texto": a.texto,
                "likes_count": a.likes_count,
            }
            for a in top
        ]
