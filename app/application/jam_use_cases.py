"""Use cases for collaborative Jam sessions and queue voting."""

import secrets
import string
from typing import Any

from app.domain.constants import IDADE_MINIMA_ADULTO
from app.domain.entities import Jam, JamFila
from app.domain.exceptions import (
    BusinessRuleViolationError,
    EntityNotFoundError,
    ForbiddenError,
)
from app.domain.ports import (
    JamRepositoryPort,
    MusicaRepositoryPort,
    UsuarioRepositoryPort,
)


def _gerar_codigo_sala() -> str:
    """Gera código alfanumérico curto para a sala."""
    caracteres = string.ascii_uppercase + string.digits
    sufixo = "".join(secrets.choice(caracteres) for _ in range(6))
    return f"JAM-{sufixo}"


class JamUseCases:
    """Casos de uso para gerenciamento de salas colaborativas de Jam."""

    def __init__(
        self,
        jam_repo: JamRepositoryPort,
        usuario_repo: UsuarioRepositoryPort,
        musica_repo: MusicaRepositoryPort,
    ) -> None:
        self.jam_repo = jam_repo
        self.usuario_repo = usuario_repo
        self.musica_repo = musica_repo

    def criar_jam(self, host_usuario_id: int, nome_sala: str) -> Jam:
        """Cria nova sala de Jam colaborativa com código exclusivo."""
        host = self.usuario_repo.buscar_por_id(host_usuario_id)
        if not host:
            raise EntityNotFoundError(f"Usuário host {host_usuario_id} não encontrado.")

        codigo = _gerar_codigo_sala()
        jam = Jam(
            jam_id=None,
            host_usuario_id=host_usuario_id,
            nome_sala=nome_sala.strip(),
            codigo_sala=codigo,
            is_ativa=True,
            musica_atual_id=None,
        )
        return self.jam_repo.salvar(jam)

    def entrar_na_jam(self, codigo_sala: str) -> Jam:
        """Busca sala ativa através do código de convite."""
        jam = self.jam_repo.buscar_por_codigo(codigo_sala.strip().upper())
        if not jam or not jam.is_ativa:
            raise EntityNotFoundError("Sala não encontrada ou inativa.")
        return jam

    def votar_musica_fila(
        self, jam_id: int, musica_id: int, usuario_id: int, pontos: int = 1
    ) -> JamFila:
        """Adiciona música ou incrementa pontuação de votos na fila da Jam."""
        usuario = self.usuario_repo.buscar_por_id(usuario_id)
        if not usuario:
            raise EntityNotFoundError(f"Usuário com ID {usuario_id} não encontrado.")

        jam = self.jam_repo.buscar_por_id(jam_id)
        if not jam or not jam.is_ativa:
            raise EntityNotFoundError("Jam não encontrada ou inativa.")

        musica = self.musica_repo.buscar_por_id(musica_id)
        if not musica or musica.is_deleted:
            raise EntityNotFoundError("Música não encontrada ou inativa.")
        if usuario.idade < IDADE_MINIMA_ADULTO and musica.bloqueado_para_menores:
            raise BusinessRuleViolationError(
                "Música bloqueada para usuários menores de idade."
            )

        return self.jam_repo.adicionar_musica_fila(jam_id, musica_id, pontos=pontos)

    def votar_musica_pular(
        self, jam_id: int, musica_id: int, usuario_id: int
    ) -> JamFila | None:
        """Vota democraticamente para pular/penalizar música na fila."""
        usuario = self.usuario_repo.buscar_por_id(usuario_id)
        if not usuario:
            raise EntityNotFoundError(f"Usuário com ID {usuario_id} não encontrado.")

        jam = self.jam_repo.buscar_por_id(jam_id)
        if not jam or not jam.is_ativa:
            raise EntityNotFoundError("Jam não encontrada ou inativa.")

        musica = self.musica_repo.buscar_por_id(musica_id)
        if not musica or musica.is_deleted:
            raise EntityNotFoundError("Música não encontrada ou inativa.")
        if usuario.idade < IDADE_MINIMA_ADULTO and musica.bloqueado_para_menores:
            raise BusinessRuleViolationError(
                "Música bloqueada para usuários menores de idade."
            )

        return self.jam_repo.atualizar_voto_musica(jam_id, musica_id, delta_pontos=-1)

    def obter_estado_e_checar_progresso(
        self, jam_id: int, usuario_id: int
    ) -> dict[str, Any]:
        """Retorna o estado atual da Jam, faixa em reprodução e fila ordenada."""
        usuario = self.usuario_repo.buscar_por_id(usuario_id)
        if not usuario:
            raise EntityNotFoundError(f"Usuário com ID {usuario_id} não encontrado.")

        jam = self.jam_repo.buscar_por_id(jam_id)
        if not jam:
            raise EntityNotFoundError("Jam não encontrada.")

        fila = self.jam_repo.listar_fila(jam_id)
        musica_atual = None
        if jam.musica_atual_id:
            musica_atual = self.musica_repo.buscar_por_id(jam.musica_atual_id)

        if usuario.idade < IDADE_MINIMA_ADULTO:
            fila = [
                item
                for item in fila
                if (
                    musica := self.musica_repo.buscar_por_id(item.musica_id)
                )
                and not musica.is_deleted
                and not musica.bloqueado_para_menores
            ]
            if musica_atual and (
                musica_atual.is_deleted or musica_atual.bloqueado_para_menores
            ):
                musica_atual = None
                jam.musica_atual_id = None

        return {
            "jam": jam,
            "musica_atual": musica_atual,
            "fila": fila,
        }

    def iniciar_ou_avancar_jam(
        self, jam_id: int, solicitante_usuario_id: int | None = None
    ) -> Jam:
        """Avança a reprodução promovendo a campeã de votos da fila."""
        jam = self.jam_repo.buscar_por_id(jam_id)
        if not jam or not jam.is_ativa:
            raise EntityNotFoundError("Jam não encontrada ou inativa.")

        if solicitante_usuario_id is not None and jam.host_usuario_id != solicitante_usuario_id:
            raise ForbiddenError("Apenas o host da sala pode avançar a reprodução da Jam.")

        fila = self.jam_repo.listar_fila(jam_id)
        if not fila:
            raise BusinessRuleViolationError("Não há músicas na fila para avançar.")

        campea = fila[0]
        jam.musica_atual_id = campea.musica_id
        salva = self.jam_repo.salvar(jam)
        self.jam_repo.remover_musica_fila(jam_id, campea.musica_id)
        return salva
