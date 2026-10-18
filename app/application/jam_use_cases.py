"""Use cases for collaborative Jam sessions and queue voting."""

import secrets
import string
from typing import Any

from app.application.exceptions import (
    BusinessRuleViolationError,
    EntityNotFoundError,
    ForbiddenError,
)
from app.domain.entities import Interacao, Jam, JamFila, Musica, Usuario
from app.domain.ports import (
    InteracaoRepositoryPort,
    JamRepositoryPort,
    MusicaRepositoryPort,
    PlaylistRepositoryPort,
    UsuarioRepositoryPort,
)


def _gerar_codigo_sala() -> str:
    """Gera código curto e numérico de convite."""
    return "".join(secrets.choice(string.digits) for _ in range(6))


class JamUseCases:
    """Casos de uso para gerenciamento de salas colaborativas de Jam."""

    def __init__(
        self,
        jam_repo: JamRepositoryPort,
        usuario_repo: UsuarioRepositoryPort,
        musica_repo: MusicaRepositoryPort,
        interacao_repo: InteracaoRepositoryPort,
        playlist_repo: PlaylistRepositoryPort,
    ) -> None:
        self.jam_repo = jam_repo
        self.usuario_repo = usuario_repo
        self.musica_repo = musica_repo
        self.interacao_repo = interacao_repo
        self.playlist_repo = playlist_repo

    def _obter_usuario(self, usuario_id: int) -> Usuario:
        usuario = self.usuario_repo.buscar_por_id(usuario_id)
        if not usuario:
            raise EntityNotFoundError(f"Usuário com ID {usuario_id} não encontrado.")
        return usuario

    def _obter_jam_ativa(self, jam_id: int) -> Jam:
        jam = self.jam_repo.buscar_por_id(jam_id)
        if not jam or not jam.is_ativa:
            raise EntityNotFoundError("Jam não encontrada ou inativa.")
        return jam

    def _validar_participante(self, jam_id: int, usuario_id: int) -> Usuario:
        usuario = self._obter_usuario(usuario_id)
        if not self.jam_repo.eh_participante(jam_id, usuario_id):
            raise ForbiddenError("É necessário entrar na sala antes de interagir.")
        return usuario

    @staticmethod
    def _validar_musica_para_usuario(usuario: Usuario, musica: Musica) -> None:
        if musica.is_deleted:
            raise EntityNotFoundError("Música não encontrada ou inativa.")
        if usuario.eh_menor_de_idade() and musica.bloqueado_para_menores:
            raise BusinessRuleViolationError(
                "Música bloqueada para usuários menores de idade."
            )
        if musica.genero.strip().lower() in usuario.lista_generos_bloqueados():
            raise BusinessRuleViolationError("Gênero bloqueado pelo usuário.")

    def criar_jam(
        self,
        host_usuario_id: int,
        nome_sala: str,
        duracao_minutos: int = 60,
        limite_superlikes: int = 10,
        meta_votos_pular: int = 3,
        fonte_deck: str = "livre",
        playlist_origem_id: int | None = None,
    ) -> Jam:
        """Cria sala com regras explícitas e registra o host como participante."""
        host = self._obter_usuario(host_usuario_id)
        fonte = fonte_deck.strip().lower()
        if fonte not in ("livre", "curtidas", "playlist"):
            raise BusinessRuleViolationError(
                "Fonte do deck deve ser livre, curtidas ou playlist."
            )
        if fonte == "playlist":
            if playlist_origem_id is None:
                raise BusinessRuleViolationError(
                    "Selecione uma playlist como fonte do deck."
                )
            playlist = self.playlist_repo.buscar_por_id(playlist_origem_id)
            if not playlist or playlist.usuario_id != host_usuario_id:
                raise ForbiddenError("A playlist de origem não pertence ao host.")
        jam = self.jam_repo.salvar(
            Jam(
                jam_id=None,
                host_usuario_id=host_usuario_id,
                nome_sala=nome_sala.strip(),
                codigo_sala=_gerar_codigo_sala(),
                is_ativa=True,
                duracao_minutos=duracao_minutos,
                limite_superlikes=limite_superlikes,
                meta_votos_pular=meta_votos_pular,
                fonte_deck=fonte,
                playlist_origem_id=playlist_origem_id,
            )
        )
        if jam.jam_id is None:
            raise BusinessRuleViolationError("Não foi possível criar a sala.")
        self.jam_repo.adicionar_participante(jam.jam_id, host.usuario_id)
        return jam

    def entrar_na_jam(self, codigo_sala: str, usuario_id: int) -> Jam:
        """Entra em uma sala ativa através do código numérico."""
        usuario = self._obter_usuario(usuario_id)
        jam = self.jam_repo.buscar_por_codigo(codigo_sala.strip())
        if not jam or not jam.is_ativa:
            raise EntityNotFoundError("Sala não encontrada ou inativa.")
        self.jam_repo.adicionar_participante(jam.jam_id, usuario.usuario_id)
        return jam

    def obter_deck_adicionar(
        self,
        jam_id: int,
        usuario_id: int,
        limite: int = 20,
        cursor_id: int | None = None,
    ) -> tuple[list[Musica], int | None, bool]:
        """Return a cursor page of eligible suggestions for a Jam participant."""
        jam = self._obter_jam_ativa(jam_id)
        usuario = self._validar_participante(jam_id, usuario_id)
        ids_rejeitadas = {
            interacao.musica_id
            for interacao in self.interacao_repo.listar_por_usuario(
                usuario_id, acao="rejeitada"
            )
        }
        if jam.fonte_deck == "playlist" and jam.playlist_origem_id:
            playlist = self.playlist_repo.buscar_por_id(jam.playlist_origem_id)
            musicas = playlist.musicas if playlist else []
        elif jam.fonte_deck == "curtidas":
            musicas = []
            for item in self.interacao_repo.listar_por_usuario(usuario_id):
                if item.acao in ("curtida", "amada"):
                    musica = self.musica_repo.buscar_por_id(item.musica_id)
                    if musica:
                        musicas.append(musica)
        else:
            musicas = []
        ids_na_sala = {item.musica_id for item in self.jam_repo.listar_fila(jam_id)}
        if jam.musica_atual_id:
            ids_na_sala.add(jam.musica_atual_id)
        ids_excluidos = ids_na_sala | ids_rejeitadas
        if jam.fonte_deck == "livre":
            musicas = self.musica_repo.listar_ativas(
                generos_excluidos=usuario.lista_generos_bloqueados(),
                bloquear_menores=usuario.eh_menor_de_idade(),
                ids_excluidos=list(ids_excluidos),
                limite=limite + 1,
                cursor_id=cursor_id,
            )
            has_more = len(musicas) > limite
            items = musicas[:limite]
            next_cursor = items[-1].musica_id if has_more and items else None
            return items, next_cursor, has_more

        elegiveis = [
            musica
            for musica in musicas
            if musica.musica_id not in ids_excluidos
            and not musica.is_deleted
            and not (usuario.eh_menor_de_idade() and musica.bloqueado_para_menores)
            and musica.genero.strip().lower() not in usuario.lista_generos_bloqueados()
        ]
        pagina = sorted(
            (
                musica
                for musica in elegiveis
                if musica.musica_id is not None
                and (cursor_id is None or musica.musica_id > cursor_id)
            ),
            key=lambda musica: musica.musica_id,
        )
        has_more = len(pagina) > limite
        items = pagina[:limite]
        next_cursor = items[-1].musica_id if has_more else None
        return items, next_cursor, has_more

    def interagir_deck(
        self, jam_id: int, musica_id: int, usuario_id: int, acao: str
    ) -> JamFila:
        """Pontua uma sugestão com like (+1) ou superlike (+2)."""
        jam = self._obter_jam_ativa(jam_id)
        usuario = self._validar_participante(jam_id, usuario_id)
        musica = self.musica_repo.buscar_por_id(musica_id)
        if not musica:
            raise EntityNotFoundError("Música não encontrada.")
        self._validar_musica_para_usuario(usuario, musica)
        normalizada = acao.strip().lower()
        if normalizada not in ("like", "curtida", "superlike", "amada"):
            raise BusinessRuleViolationError("Ação deve ser like ou superlike.")
        superlike = normalizada in ("superlike", "amada")
        if superlike and jam.superlikes_usados >= jam.limite_superlikes:
            raise BusinessRuleViolationError(
                "O limite de superlikes desta sala foi atingido."
            )
        duracao_enfileirada = sum(
            item.duracao_segundos
            for item in (
                self.musica_repo.buscar_por_id(faixa.musica_id)
                for faixa in self.jam_repo.listar_fila(jam_id)
            )
            if item
        )
        if jam.musica_atual_id:
            musica_atual = self.musica_repo.buscar_por_id(jam.musica_atual_id)
            if musica_atual:
                duracao_enfileirada += musica_atual.duracao_segundos
        if (
            jam.duracao_acumulada_segundos
            + duracao_enfileirada
            + musica.duracao_segundos
            > jam.duracao_minutos * 60
        ):
            raise BusinessRuleViolationError(
                "A faixa ultrapassaria a duração configurada para a Jam."
            )
        fila = self.jam_repo.adicionar_musica_fila(
            jam_id, musica_id, pontos=2 if superlike else 1
        )
        if superlike:
            jam.superlikes_usados += 1
            self.jam_repo.salvar(jam)
        if jam.musica_atual_id is None:
            self._avancar(jam)
        return fila

    def votar_musica_pular(
        self, jam_id: int, usuario_id: int, musica_id: int | None = None
    ) -> dict[str, Any]:
        """Registra voto único na faixa atual e avança ao atingir a meta."""
        jam = self._obter_jam_ativa(jam_id)
        usuario = self._validar_participante(jam_id, usuario_id)
        atual_id = jam.musica_atual_id
        if atual_id is None:
            raise BusinessRuleViolationError("Não há faixa atual para votar.")
        if musica_id is not None and musica_id != atual_id:
            raise BusinessRuleViolationError("O voto deve ser na faixa atual.")
        musica = self.musica_repo.buscar_por_id(atual_id)
        if not musica:
            raise EntityNotFoundError("Faixa atual não encontrada.")
        self._validar_musica_para_usuario(usuario, musica)
        votos = self.jam_repo.registrar_voto_pular(jam_id, atual_id, usuario_id)
        avancou = votos >= jam.meta_votos_pular
        if avancou:
            self._avancar(jam)
        return {
            "jam_id": jam_id,
            "musica_id": atual_id,
            "votos": votos,
            "meta": jam.meta_votos_pular,
            "avancou": avancou,
            "jam_ativa": jam.is_ativa,
        }

    def _avancar(self, jam: Jam) -> None:
        """Atualiza duração e promove a faixa mais votada."""
        faixa_anterior = jam.musica_atual_id
        if faixa_anterior:
            musica_anterior = self.musica_repo.buscar_por_id(faixa_anterior)
            if musica_anterior:
                jam.duracao_acumulada_segundos += musica_anterior.duracao_segundos
            self.jam_repo.limpar_votos_pular(jam.jam_id, faixa_anterior)
        if jam.duracao_acumulada_segundos >= jam.duracao_minutos * 60:
            jam.is_ativa = False
            jam.musica_atual_id = None
            self.jam_repo.salvar(jam)
            return
        fila = self.jam_repo.listar_fila(jam.jam_id)
        if not fila:
            jam.musica_atual_id = None
            self.jam_repo.salvar(jam)
            return
        campea = fila[0]
        jam.musica_atual_id = campea.musica_id
        self.jam_repo.remover_musica_fila(jam.jam_id, campea.musica_id)
        self.jam_repo.salvar(jam)

    def salvar_faixa_fila(
        self,
        jam_id: int,
        usuario_id: int,
        musica_id: int,
        playlist_id: int | None = None,
    ) -> bool:
        """Salva uma faixa da sala nas amadas e, opcionalmente, em playlist."""
        usuario = self._validar_participante(jam_id, usuario_id)
        jam = self._obter_jam_ativa(jam_id)
        musicas_sala = {item.musica_id for item in self.jam_repo.listar_fila(jam_id)}
        if jam.musica_atual_id:
            musicas_sala.add(jam.musica_atual_id)
        if musica_id not in musicas_sala:
            raise EntityNotFoundError("Música não pertence à fila desta Jam.")
        musica = self.musica_repo.buscar_por_id(musica_id)
        if not musica:
            raise EntityNotFoundError("Música não encontrada.")
        self._validar_musica_para_usuario(usuario, musica)
        if playlist_id is not None:
            playlist = self.playlist_repo.buscar_por_id(playlist_id)
            if not playlist:
                raise EntityNotFoundError("Playlist não encontrada.")
            if playlist.usuario_id != usuario_id:
                raise ForbiddenError("A playlist não pertence a este usuário.")
            self.playlist_repo.adicionar_musica(playlist_id, musica_id)
        self.interacao_repo.salvar(
            Interacao(
                interacao_id=None,
                usuario_id=usuario_id,
                musica_id=musica_id,
                acao="amada",
            )
        )
        return True

    def obter_estado_e_checar_progresso(
        self, jam_id: int, usuario_id: int
    ) -> dict[str, Any]:
        """Retorna estado seguro da sala para o participante autenticado."""
        usuario = self._validar_participante(jam_id, usuario_id)
        jam = self.jam_repo.buscar_por_id(jam_id)
        if not jam:
            raise EntityNotFoundError("Jam não encontrada.")
        fila: list[JamFila] = []
        for item in self.jam_repo.listar_fila(jam_id):
            musica = self.musica_repo.buscar_por_id(item.musica_id)
            if musica:
                try:
                    self._validar_musica_para_usuario(usuario, musica)
                except BusinessRuleViolationError:
                    continue
                fila.append(item)
        musica_atual = (
            self.musica_repo.buscar_por_id(jam.musica_atual_id)
            if jam.musica_atual_id
            else None
        )
        if musica_atual:
            try:
                self._validar_musica_para_usuario(usuario, musica_atual)
            except BusinessRuleViolationError:
                musica_atual = None
        votos = (
            self.jam_repo.contar_votos_pular(jam_id, jam.musica_atual_id)
            if jam.musica_atual_id
            else 0
        )
        return {
            "jam": jam,
            "musica_atual": musica_atual,
            "fila": fila,
            "votos_pular": votos,
        }

    def encerrar_jam(self, jam_id: int, host_usuario_id: int) -> Jam:
        """Permite exclusivamente ao host encerrar a sala."""
        jam = self._obter_jam_ativa(jam_id)
        if jam.host_usuario_id != host_usuario_id:
            raise ForbiddenError("Apenas o host pode encerrar a Jam.")
        jam.is_ativa = False
        return self.jam_repo.salvar(jam)
