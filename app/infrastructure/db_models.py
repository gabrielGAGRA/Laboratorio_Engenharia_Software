"""SQLAlchemy declarative models for Ribbit database tables."""

from datetime import UTC, datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.infrastructure.database import Base


def _utc_now() -> datetime:
    return datetime.now(UTC)


class PlanoModel(Base):
    """Modelo ORM da tabela planos."""

    __tablename__ = "planos"

    plano_id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), unique=True, nullable=False)
    preco_mensal = Column(Float, nullable=False)
    max_perfis = Column(Integer, nullable=False, default=1)

    usuarios = relationship("UsuarioModel", back_populates="plano")


class UsuarioModel(Base):
    """Modelo ORM da tabela usuarios."""

    __tablename__ = "usuarios"

    usuario_id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    senha_hash = Column(String(255), nullable=False)
    spotify_id = Column(String(64), unique=True, nullable=True)
    nome_exibicao = Column(String(150), nullable=False)
    idade = Column(Integer, nullable=False)
    plano_id = Column(Integer, ForeignKey("planos.plano_id"), nullable=False)
    titular_id = Column(Integer, ForeignKey("usuarios.usuario_id"), nullable=True)
    generos_bloqueados = Column(Text, nullable=True)
    is_admin = Column(Boolean, nullable=False, default=False)
    criado_em = Column(DateTime(timezone=True), default=_utc_now, nullable=False)

    plano = relationship("PlanoModel", back_populates="usuarios")
    titular = relationship(
        "UsuarioModel", remote_side=[usuario_id], backref="dependentes"
    )
    interacoes = relationship(
        "InteracaoModel", back_populates="usuario", cascade="all, delete-orphan"
    )
    playlists = relationship(
        "PlaylistModel", back_populates="usuario", cascade="all, delete-orphan"
    )
    avaliacoes = relationship(
        "AvaliacaoComentarioModel",
        back_populates="usuario",
        cascade="all, delete-orphan",
    )


class MusicaModel(Base):
    """Modelo ORM da tabela musicas."""

    __tablename__ = "musicas"

    musica_id = Column(Integer, primary_key=True, autoincrement=True)
    spotify_id = Column(String(64), nullable=True)
    titulo = Column(String(255), nullable=False, index=True)
    artista = Column(String(255), nullable=False, index=True)
    album = Column(String(255), nullable=True)
    duracao_segundos = Column(Integer, nullable=False)
    genero = Column(String(100), nullable=False, index=True)
    pais = Column(String(100), nullable=True)
    ano_lancamento = Column(Integer, nullable=True)
    capa_url = Column(Text, nullable=True)
    itunes_preview_url = Column(Text, nullable=True)
    bloqueado_para_menores = Column(Boolean, nullable=False, default=False)
    is_deleted = Column(Boolean, nullable=False, default=False)
    criado_em = Column(DateTime(timezone=True), default=_utc_now, nullable=False)

    interacoes = relationship("InteracaoModel", back_populates="musica")
    playlist_itens = relationship("PlaylistMusicaModel", back_populates="musica")
    fila_itens = relationship("JamFilaModel", back_populates="musica")
    avaliacoes = relationship("AvaliacaoComentarioModel", back_populates="musica")


class InteracaoModel(Base):
    """Modelo ORM da tabela interacoes."""

    __tablename__ = "interacoes"
    __table_args__ = (
        UniqueConstraint(
            "usuario_id", "musica_id", name="uq_interacoes_usuario_musica"
        ),
    )

    interacao_id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(
        Integer, ForeignKey("usuarios.usuario_id", ondelete="CASCADE"), nullable=False
    )
    musica_id = Column(Integer, ForeignKey("musicas.musica_id"), nullable=False)
    acao = Column(String(50), nullable=False)
    criado_em = Column(DateTime(timezone=True), default=_utc_now, nullable=False)

    usuario = relationship("UsuarioModel", back_populates="interacoes")
    musica = relationship("MusicaModel", back_populates="interacoes")


class PlaylistModel(Base):
    """Modelo ORM da tabela playlists."""

    __tablename__ = "playlists"

    playlist_id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(
        Integer, ForeignKey("usuarios.usuario_id", ondelete="CASCADE"), nullable=False
    )
    nome = Column(String(255), nullable=False)
    descricao = Column(Text, nullable=True)
    spotify_playlist_id = Column(String(64), nullable=True)
    is_exportada = Column(Boolean, default=False, nullable=False)
    criado_em = Column(DateTime(timezone=True), default=_utc_now, nullable=False)

    usuario = relationship("UsuarioModel", back_populates="playlists")
    itens = relationship(
        "PlaylistMusicaModel", back_populates="playlist", cascade="all, delete-orphan"
    )


class PlaylistMusicaModel(Base):
    """Modelo associativo da tabela playlist_musicas."""

    __tablename__ = "playlist_musicas"
    __table_args__ = (
        UniqueConstraint("playlist_id", "musica_id", name="uq_playlist_musicas_item"),
    )

    playlist_musica_id = Column(Integer, primary_key=True, autoincrement=True)
    playlist_id = Column(
        Integer, ForeignKey("playlists.playlist_id", ondelete="CASCADE"), nullable=False
    )
    musica_id = Column(Integer, ForeignKey("musicas.musica_id"), nullable=False)
    adicionado_em = Column(DateTime(timezone=True), default=_utc_now, nullable=False)

    playlist = relationship("PlaylistModel", back_populates="itens")
    musica = relationship("MusicaModel", back_populates="playlist_itens")


class JamModel(Base):
    """Modelo ORM da tabela jams."""

    __tablename__ = "jams"

    jam_id = Column(Integer, primary_key=True, autoincrement=True)
    host_usuario_id = Column(
        Integer, ForeignKey("usuarios.usuario_id", ondelete="CASCADE"), nullable=False
    )
    nome_sala = Column(String(150), nullable=False)
    codigo_sala = Column(String(32), unique=True, nullable=False)
    is_ativa = Column(Boolean, default=True, nullable=False)
    musica_atual_id = Column(Integer, ForeignKey("musicas.musica_id"), nullable=True)
    criado_em = Column(DateTime(timezone=True), default=_utc_now, nullable=False)

    fila = relationship(
        "JamFilaModel", back_populates="jam", cascade="all, delete-orphan"
    )


class JamFilaModel(Base):
    """Modelo ORM da tabela jam_fila."""

    __tablename__ = "jam_fila"
    __table_args__ = (
        UniqueConstraint("jam_id", "musica_id", name="uq_jam_fila_jam_musica"),
    )

    jam_fila_id = Column(Integer, primary_key=True, autoincrement=True)
    jam_id = Column(
        Integer, ForeignKey("jams.jam_id", ondelete="CASCADE"), nullable=False
    )
    musica_id = Column(Integer, ForeignKey("musicas.musica_id"), nullable=False)
    pontos_voto = Column(Integer, default=0, nullable=False)
    adicionado_em = Column(DateTime(timezone=True), default=_utc_now, nullable=False)

    jam = relationship("JamModel", back_populates="fila")
    musica = relationship("MusicaModel", back_populates="fila_itens")


class AvaliacaoComentarioModel(Base):
    """Modelo ORM da tabela avaliacoes_comentarios."""

    __tablename__ = "avaliacoes_comentarios"

    avaliacao_id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(
        Integer, ForeignKey("usuarios.usuario_id", ondelete="CASCADE"), nullable=False
    )
    musica_id = Column(Integer, ForeignKey("musicas.musica_id"), nullable=False)
    nota = Column(Integer, nullable=False)
    texto = Column(Text, nullable=True)
    likes_count = Column(Integer, default=0, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    criado_em = Column(DateTime(timezone=True), default=_utc_now, nullable=False)

    usuario = relationship("UsuarioModel", back_populates="avaliacoes")
    musica = relationship("MusicaModel", back_populates="avaliacoes")
