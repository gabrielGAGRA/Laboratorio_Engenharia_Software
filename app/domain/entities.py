"""Domain entities for Ribbit platform. Pure Python dataclasses."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum


class AcaoInteracao(StrEnum):
    """Ações permitidas para interação por swipe."""

    CURTIDA = "curtida"
    AMADA = "amada"
    REJEITADA = "rejeitada"


@dataclass(slots=True)
class Plano:
    """Entidade de plano de assinatura."""

    plano_id: int | None
    nome: str
    preco_mensal: float
    max_perfis: int = 1


@dataclass(slots=True)
class Usuario:
    """Entidade de usuário."""

    usuario_id: int | None
    email: str
    senha_hash: str
    nome_exibicao: str
    idade: int
    plano_id: int
    spotify_id: str | None = None
    titular_id: int | None = None
    generos_bloqueados: str | None = None
    is_admin: bool = False
    criado_em: datetime | None = None

    def lista_generos_bloqueados(self) -> list[str]:
        """Retorna lista normalizada de gêneros bloqueados."""
        if not self.generos_bloqueados:
            return []
        return [
            g.strip().lower() for g in self.generos_bloqueados.split(",") if g.strip()
        ]


@dataclass(slots=True)
class Musica:
    """Entidade de música."""

    musica_id: int | None
    titulo: str
    artista: str
    duracao_segundos: int
    genero: str
    spotify_id: str | None = None
    album: str | None = None
    pais: str | None = None
    ano_lancamento: int | None = None
    capa_url: str | None = None
    itunes_preview_url: str | None = None
    bloqueado_para_menores: bool = False
    is_deleted: bool = False
    criado_em: datetime | None = None


@dataclass(slots=True)
class Interacao:
    """Entidade de interação (swipe) do usuário com uma faixa."""

    interacao_id: int | None
    usuario_id: int
    musica_id: int
    acao: str
    criado_em: datetime | None = None


@dataclass(slots=True)
class Playlist:
    """Entidade de playlist do usuário."""

    playlist_id: int | None
    usuario_id: int
    nome: str
    descricao: str | None = None
    spotify_playlist_id: str | None = None
    is_exportada: bool = False
    criado_em: datetime | None = None
    musicas: list[Musica] = field(default_factory=list)


@dataclass(slots=True)
class PlaylistMusica:
    """Associação de faixa à playlist."""

    playlist_musica_id: int | None
    playlist_id: int
    musica_id: int
    adicionado_em: datetime | None = None


@dataclass(slots=True)
class Jam:
    """Entidade de sala de Jam colaborativa."""

    jam_id: int | None
    host_usuario_id: int
    nome_sala: str
    codigo_sala: str
    is_ativa: bool = True
    musica_atual_id: int | None = None
    criado_em: datetime | None = None


@dataclass(slots=True)
class JamFila:
    """Item da fila de votação da Jam."""

    jam_fila_id: int | None
    jam_id: int
    musica_id: int
    pontos_voto: int = 0
    adicionado_em: datetime | None = None


@dataclass(slots=True)
class AvaliacaoComentario:
    """Avaliação/comentário de uma faixa na comunidade."""

    avaliacao_id: int | None
    usuario_id: int
    musica_id: int
    nota: int
    texto: str | None = None
    likes_count: int = 0
    is_deleted: bool = False
    criado_em: datetime | None = None
