"""Concrete repository implementations mapping SQLAlchemy models to Domain entities."""

from datetime import UTC, date, datetime, timedelta

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.domain.entities import (
    AvaliacaoComentario,
    Interacao,
    Jam,
    JamFila,
    Musica,
    Plano,
    Playlist,
    Usuario,
)
from app.domain.ports import (
    AvaliacaoRepositoryPort,
    InteracaoRepositoryPort,
    JamRepositoryPort,
    MusicaRepositoryPort,
    PlanoRepositoryPort,
    PlaylistRepositoryPort,
    UsuarioRepositoryPort,
)
from app.infrastructure.db_models import (
    AvaliacaoComentarioModel,
    AvaliacaoCurtidaModel,
    InteracaoModel,
    JamFilaModel,
    JamModel,
    JamParticipanteModel,
    JamVotoPularModel,
    MusicaModel,
    PlanoModel,
    PlaylistModel,
    PlaylistMusicaModel,
    UsuarioModel,
)


def _to_usuario_entity(model: UsuarioModel) -> Usuario:
    idade = model.idade
    if model.data_nascimento:
        hoje = date.today()
        idade = (
            hoje.year
            - model.data_nascimento.year
            - (
                (hoje.month, hoje.day)
                < (model.data_nascimento.month, model.data_nascimento.day)
            )
        )
    return Usuario(
        usuario_id=model.usuario_id,
        email=model.email,
        senha_hash=model.senha_hash,
        nome_exibicao=model.nome_exibicao,
        idade=idade,
        plano_id=model.plano_id,
        spotify_id=model.spotify_id,
        titular_id=model.titular_id,
        generos_bloqueados=model.generos_bloqueados,
        is_admin=model.is_admin,
        criado_em=model.criado_em,
        data_nascimento=model.data_nascimento,
    )


def _to_plano_entity(model: PlanoModel) -> Plano:
    return Plano(
        plano_id=model.plano_id,
        nome=model.nome,
        preco_mensal=float(model.preco_mensal),
        max_perfis=model.max_perfis,
    )


def _to_musica_entity(model: MusicaModel) -> Musica:
    return Musica(
        musica_id=model.musica_id,
        titulo=model.titulo,
        artista=model.artista,
        duracao_segundos=model.duracao_segundos,
        genero=model.genero,
        spotify_id=model.spotify_id,
        album=model.album,
        pais=model.pais,
        ano_lancamento=model.ano_lancamento,
        capa_url=model.capa_url,
        itunes_preview_url=model.itunes_preview_url,
        bloqueado_para_menores=model.bloqueado_para_menores,
        is_deleted=model.is_deleted,
        criado_em=model.criado_em,
    )


def _to_interacao_entity(model: InteracaoModel) -> Interacao:
    return Interacao(
        interacao_id=model.interacao_id,
        usuario_id=model.usuario_id,
        musica_id=model.musica_id,
        acao=model.acao,
        criado_em=model.criado_em,
    )


def _to_playlist_entity(
    model: PlaylistModel, musicas: list[Musica] | None = None
) -> Playlist:
    return Playlist(
        playlist_id=model.playlist_id,
        usuario_id=model.usuario_id,
        nome=model.nome,
        descricao=model.descricao,
        spotify_playlist_id=model.spotify_playlist_id,
        is_exportada=model.is_exportada,
        criado_em=model.criado_em,
        musicas=musicas or [],
        duracao_maxima_segundos=model.duracao_maxima_segundos,
        filtros_deck=model.filtros_deck,
    )


def _to_jam_entity(model: JamModel) -> Jam:
    return Jam(
        jam_id=model.jam_id,
        host_usuario_id=model.host_usuario_id,
        nome_sala=model.nome_sala,
        codigo_sala=model.codigo_sala,
        is_ativa=model.is_ativa,
        musica_atual_id=model.musica_atual_id,
        criado_em=model.criado_em,
        duracao_minutos=model.duracao_minutos,
        limite_superlikes=model.limite_superlikes,
        superlikes_usados=model.superlikes_usados,
        meta_votos_pular=model.meta_votos_pular,
        duracao_acumulada_segundos=model.duracao_acumulada_segundos,
        fonte_deck=model.fonte_deck,
        playlist_origem_id=model.playlist_origem_id,
    )


def _to_jam_fila_entity(model: JamFilaModel) -> JamFila:
    return JamFila(
        jam_fila_id=model.jam_fila_id,
        jam_id=model.jam_id,
        musica_id=model.musica_id,
        pontos_voto=model.pontos_voto,
        adicionado_em=model.adicionado_em,
    )


def _to_avaliacao_entity(model: AvaliacaoComentarioModel) -> AvaliacaoComentario:
    return AvaliacaoComentario(
        avaliacao_id=model.avaliacao_id,
        usuario_id=model.usuario_id,
        musica_id=model.musica_id,
        nota=model.nota,
        texto=model.texto,
        likes_count=model.likes_count,
        is_deleted=model.is_deleted,
        criado_em=model.criado_em,
    )


class UsuarioRepository(UsuarioRepositoryPort):
    """Implementação do repositório de usuários via SQLAlchemy."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def buscar_por_id(self, usuario_id: int) -> Usuario | None:
        model = (
            self.session.query(UsuarioModel)
            .filter(UsuarioModel.usuario_id == usuario_id)
            .first()
        )
        return _to_usuario_entity(model) if model else None

    def buscar_por_email(self, email: str) -> Usuario | None:
        model = (
            self.session.query(UsuarioModel)
            .filter(func.lower(UsuarioModel.email) == email.lower().strip())
            .first()
        )
        return _to_usuario_entity(model) if model else None

    def salvar(self, usuario: Usuario) -> Usuario:
        if usuario.usuario_id:
            model = (
                self.session.query(UsuarioModel)
                .filter(UsuarioModel.usuario_id == usuario.usuario_id)
                .first()
            )
            if model:
                model.email = usuario.email.lower().strip()
                model.senha_hash = usuario.senha_hash
                model.nome_exibicao = usuario.nome_exibicao
                model.idade = usuario.idade
                model.plano_id = usuario.plano_id
                model.spotify_id = usuario.spotify_id
                model.titular_id = usuario.titular_id
                model.generos_bloqueados = usuario.generos_bloqueados
                model.is_admin = usuario.is_admin
                model.data_nascimento = usuario.data_nascimento
                self.session.commit()
                self.session.refresh(model)
                return _to_usuario_entity(model)

        model = UsuarioModel(
            email=usuario.email.lower().strip(),
            senha_hash=usuario.senha_hash,
            nome_exibicao=usuario.nome_exibicao,
            idade=usuario.idade,
            plano_id=usuario.plano_id,
            spotify_id=usuario.spotify_id,
            titular_id=usuario.titular_id,
            generos_bloqueados=usuario.generos_bloqueados,
            is_admin=usuario.is_admin,
            data_nascimento=usuario.data_nascimento,
        )
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return _to_usuario_entity(model)

    def excluir(self, usuario_id: int) -> bool:
        model = (
            self.session.query(UsuarioModel)
            .filter(UsuarioModel.usuario_id == usuario_id)
            .first()
        )
        if not model:
            return False
        self.session.delete(model)
        self.session.commit()
        return True

    def listar_dependentes(self, titular_id: int) -> list[Usuario]:
        models = (
            self.session.query(UsuarioModel)
            .filter(UsuarioModel.titular_id == titular_id)
            .all()
        )
        return [_to_usuario_entity(m) for m in models]

    def listar_todos(self) -> list[Usuario]:
        models = self.session.query(UsuarioModel).all()
        return [_to_usuario_entity(m) for m in models]


class PlanoRepository(PlanoRepositoryPort):
    """Implementação do repositório de planos."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def buscar_por_id(self, plano_id: int) -> Plano | None:
        model = (
            self.session.query(PlanoModel)
            .filter(PlanoModel.plano_id == plano_id)
            .first()
        )
        return _to_plano_entity(model) if model else None

    def buscar_por_nome(self, nome: str) -> Plano | None:
        model = (
            self.session.query(PlanoModel)
            .filter(func.lower(PlanoModel.nome) == nome.lower().strip())
            .first()
        )
        return _to_plano_entity(model) if model else None

    def listar_todos(self) -> list[Plano]:
        models = self.session.query(PlanoModel).all()
        return [_to_plano_entity(m) for m in models]

    def salvar(self, plano: Plano) -> Plano:
        if plano.plano_id:
            model = (
                self.session.query(PlanoModel)
                .filter(PlanoModel.plano_id == plano.plano_id)
                .first()
            )
            if model:
                model.nome = plano.nome
                model.preco_mensal = plano.preco_mensal
                model.max_perfis = plano.max_perfis
                self.session.commit()
                self.session.refresh(model)
                return _to_plano_entity(model)

        model = PlanoModel(
            nome=plano.nome,
            preco_mensal=plano.preco_mensal,
            max_perfis=plano.max_perfis,
        )
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return _to_plano_entity(model)


class MusicaRepository(MusicaRepositoryPort):
    """Implementação do repositório de músicas."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def buscar_por_id(self, musica_id: int) -> Musica | None:
        model = (
            self.session.query(MusicaModel)
            .filter(MusicaModel.musica_id == musica_id)
            .first()
        )
        return _to_musica_entity(model) if model else None

    def salvar(self, musica: Musica) -> Musica:
        if not musica.musica_id and musica.spotify_id:
            existente = (
                self.session.query(MusicaModel)
                .filter(MusicaModel.spotify_id == musica.spotify_id)
                .first()
            )
            if existente:
                musica.musica_id = existente.musica_id
        if musica.musica_id:
            model = (
                self.session.query(MusicaModel)
                .filter(MusicaModel.musica_id == musica.musica_id)
                .first()
            )
            if model:
                model.titulo = musica.titulo
                model.artista = musica.artista
                model.spotify_id = musica.spotify_id
                model.album = musica.album
                model.duracao_segundos = musica.duracao_segundos
                model.genero = musica.genero
                model.pais = musica.pais
                model.ano_lancamento = musica.ano_lancamento
                model.capa_url = musica.capa_url
                model.itunes_preview_url = musica.itunes_preview_url
                model.bloqueado_para_menores = musica.bloqueado_para_menores
                model.is_deleted = musica.is_deleted
                self.session.commit()
                self.session.refresh(model)
                return _to_musica_entity(model)

        model = MusicaModel(
            spotify_id=musica.spotify_id,
            titulo=musica.titulo,
            artista=musica.artista,
            album=musica.album,
            duracao_segundos=musica.duracao_segundos,
            genero=musica.genero,
            pais=musica.pais,
            ano_lancamento=musica.ano_lancamento,
            capa_url=musica.capa_url,
            itunes_preview_url=musica.itunes_preview_url,
            bloqueado_para_menores=musica.bloqueado_para_menores,
            is_deleted=musica.is_deleted,
        )
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return _to_musica_entity(model)

    def listar_ativas(
        self,
        generos_excluidos: list[str] | None = None,
        bloquear_menores: bool = False,
        ids_excluidos: list[int] | None = None,
        limite: int | None = 50,
        cursor_id: int | None = None,
    ) -> list[Musica]:
        query = self.session.query(MusicaModel).filter(
            MusicaModel.is_deleted.is_(False)
        )

        if bloquear_menores:
            query = query.filter(MusicaModel.bloqueado_para_menores.is_(False))

        if ids_excluidos:
            query = query.filter(MusicaModel.musica_id.notin_(ids_excluidos))
        if cursor_id is not None:
            query = query.filter(MusicaModel.musica_id > cursor_id)

        if generos_excluidos:
            norm_generos = [g.lower().strip() for g in generos_excluidos if g.strip()]
            if norm_generos:
                query = query.filter(
                    func.lower(MusicaModel.genero).notin_(norm_generos)
                )

        query = query.order_by(MusicaModel.musica_id)
        models = query.limit(limite).all() if limite is not None else query.all()
        return [_to_musica_entity(m) for m in models]

    def buscar_por_filtros(
        self,
        artista: str | None = None,
        album: str | None = None,
        genero: str | None = None,
        ano: int | None = None,
        pais: str | None = None,
        termo: str | None = None,
        generos_excluidos: list[str] | None = None,
        bloquear_menores: bool = False,
        ids_excluidos: list[int] | None = None,
        duracao_maxima_segundos: int | None = None,
        cursor_id: int | None = None,
        limite: int | None = None,
    ) -> list[Musica]:
        query = self.session.query(MusicaModel).filter(
            MusicaModel.is_deleted.is_(False)
        )

        if termo:
            like_term = f"%{termo.lower()}%"
            query = query.filter(
                or_(
                    func.lower(MusicaModel.titulo).like(like_term),
                    func.lower(MusicaModel.artista).like(like_term),
                    func.lower(MusicaModel.album).like(like_term),
                )
            )
        if artista:
            query = query.filter(
                func.lower(MusicaModel.artista).like(f"%{artista.lower()}%")
            )
        if album:
            query = query.filter(
                func.lower(MusicaModel.album).like(f"%{album.lower()}%")
            )
        if genero:
            query = query.filter(func.lower(MusicaModel.genero) == genero.lower())
        if ano:
            query = query.filter(MusicaModel.ano_lancamento == ano)
        if pais:
            query = query.filter(func.lower(MusicaModel.pais).like(f"%{pais.lower()}%"))

        if generos_excluidos:
            norm_generos = [item.lower().strip() for item in generos_excluidos]
            query = query.filter(func.lower(MusicaModel.genero).notin_(norm_generos))
        if bloquear_menores:
            query = query.filter(MusicaModel.bloqueado_para_menores.is_(False))
        if ids_excluidos:
            query = query.filter(MusicaModel.musica_id.notin_(ids_excluidos))
        if duracao_maxima_segundos is not None:
            query = query.filter(
                MusicaModel.duracao_segundos <= duracao_maxima_segundos
            )
        if cursor_id is not None:
            query = query.filter(MusicaModel.musica_id > cursor_id)
        query = query.order_by(MusicaModel.musica_id)
        if limite is not None:
            query = query.limit(limite)

        models = query.all()
        return [_to_musica_entity(m) for m in models]

    def contar_todas(self) -> int:
        return self.session.query(MusicaModel).count()

    def listar_bloqueadas(self) -> list[Musica]:
        models = (
            self.session.query(MusicaModel)
            .filter(MusicaModel.is_deleted.is_(True))
            .all()
        )
        return [_to_musica_entity(model) for model in models]

    def contar_ativas(self) -> int:
        return (
            self.session.query(MusicaModel)
            .filter(MusicaModel.is_deleted.is_(False))
            .count()
        )


class InteracaoRepository(InteracaoRepositoryPort):
    """Implementação do repositório de interações."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def buscar_por_usuario_e_musica(
        self, usuario_id: int, musica_id: int
    ) -> Interacao | None:
        model = (
            self.session.query(InteracaoModel)
            .filter(
                InteracaoModel.usuario_id == usuario_id,
                InteracaoModel.musica_id == musica_id,
            )
            .first()
        )
        return _to_interacao_entity(model) if model else None

    def salvar(self, interacao: Interacao) -> Interacao:
        model = (
            self.session.query(InteracaoModel)
            .filter(
                InteracaoModel.usuario_id == interacao.usuario_id,
                InteracaoModel.musica_id == interacao.musica_id,
            )
            .first()
        )
        if model:
            model.acao = interacao.acao
            self.session.commit()
            self.session.refresh(model)
            return _to_interacao_entity(model)

        model = InteracaoModel(
            usuario_id=interacao.usuario_id,
            musica_id=interacao.musica_id,
            acao=interacao.acao,
        )
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return _to_interacao_entity(model)

    def listar_por_usuario(
        self, usuario_id: int, acao: str | None = None
    ) -> list[Interacao]:
        query = self.session.query(InteracaoModel).filter(
            InteracaoModel.usuario_id == usuario_id
        )
        if acao:
            query = query.filter(InteracaoModel.acao == acao)
        models = query.order_by(InteracaoModel.criado_em.desc()).all()
        return [_to_interacao_entity(m) for m in models]

    def listar_ids_musicas_interagidas(self, usuario_id: int) -> list[int]:
        rows = (
            self.session.query(InteracaoModel.musica_id)
            .filter(InteracaoModel.usuario_id == usuario_id)
            .all()
        )
        return [r[0] for r in rows]


class PlaylistRepository(PlaylistRepositoryPort):
    """Implementação do repositório de playlists."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def buscar_por_id(self, playlist_id: int) -> Playlist | None:
        model = (
            self.session.query(PlaylistModel)
            .filter(PlaylistModel.playlist_id == playlist_id)
            .first()
        )
        if not model:
            return None
        itens = (
            self.session.query(PlaylistMusicaModel)
            .filter(PlaylistMusicaModel.playlist_id == playlist_id)
            .all()
        )
        musica_ids = [item.musica_id for item in itens]
        musicas = []
        if musica_ids:
            musica_models = (
                self.session.query(MusicaModel)
                .filter(
                    MusicaModel.musica_id.in_(musica_ids),
                    MusicaModel.is_deleted.is_(False),
                )
                .all()
            )
            musicas = [_to_musica_entity(m) for m in musica_models]
        return _to_playlist_entity(model, musicas)

    def listar_por_usuario(self, usuario_id: int) -> list[Playlist]:
        models = (
            self.session.query(PlaylistModel)
            .filter(PlaylistModel.usuario_id == usuario_id)
            .all()
        )
        return [_to_playlist_entity(m) for m in models]

    def salvar(self, playlist: Playlist) -> Playlist:
        if playlist.playlist_id:
            model = (
                self.session.query(PlaylistModel)
                .filter(PlaylistModel.playlist_id == playlist.playlist_id)
                .first()
            )
            if model:
                model.nome = playlist.nome
                model.descricao = playlist.descricao
                model.spotify_playlist_id = playlist.spotify_playlist_id
                model.is_exportada = playlist.is_exportada
                model.duracao_maxima_segundos = playlist.duracao_maxima_segundos
                model.filtros_deck = playlist.filtros_deck
                self.session.commit()
                self.session.refresh(model)
                return _to_playlist_entity(model)

        model = PlaylistModel(
            usuario_id=playlist.usuario_id,
            nome=playlist.nome,
            descricao=playlist.descricao,
            spotify_playlist_id=playlist.spotify_playlist_id,
            is_exportada=playlist.is_exportada,
            duracao_maxima_segundos=playlist.duracao_maxima_segundos,
            filtros_deck=playlist.filtros_deck,
        )
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return _to_playlist_entity(model)

    def excluir(self, playlist_id: int) -> bool:
        model = (
            self.session.query(PlaylistModel)
            .filter(PlaylistModel.playlist_id == playlist_id)
            .first()
        )
        if not model:
            return False
        self.session.delete(model)
        self.session.commit()
        return True

    def adicionar_musica(self, playlist_id: int, musica_id: int) -> bool:
        existente = (
            self.session.query(PlaylistMusicaModel)
            .filter(
                PlaylistMusicaModel.playlist_id == playlist_id,
                PlaylistMusicaModel.musica_id == musica_id,
            )
            .first()
        )
        if existente:
            return True
        item = PlaylistMusicaModel(playlist_id=playlist_id, musica_id=musica_id)
        self.session.add(item)
        self.session.commit()
        return True

    def remover_musica(self, playlist_id: int, musica_id: int) -> bool:
        item = (
            self.session.query(PlaylistMusicaModel)
            .filter(
                PlaylistMusicaModel.playlist_id == playlist_id,
                PlaylistMusicaModel.musica_id == musica_id,
            )
            .first()
        )
        if not item:
            return False
        self.session.delete(item)
        self.session.commit()
        return True


class JamRepository(JamRepositoryPort):
    """Implementação do repositório de salas colaborativas de Jam."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def buscar_por_id(self, jam_id: int) -> Jam | None:
        model = self.session.query(JamModel).filter(JamModel.jam_id == jam_id).first()
        return _to_jam_entity(model) if model else None

    def buscar_por_codigo(self, codigo_sala: str) -> Jam | None:
        model = (
            self.session.query(JamModel)
            .filter(JamModel.codigo_sala == codigo_sala, JamModel.is_ativa.is_(True))
            .first()
        )
        return _to_jam_entity(model) if model else None

    def salvar(self, jam: Jam) -> Jam:
        if jam.jam_id:
            model = (
                self.session.query(JamModel)
                .filter(JamModel.jam_id == jam.jam_id)
                .first()
            )
            if model:
                model.nome_sala = jam.nome_sala
                model.codigo_sala = jam.codigo_sala
                model.is_ativa = jam.is_ativa
                model.musica_atual_id = jam.musica_atual_id
                model.duracao_minutos = jam.duracao_minutos
                model.limite_superlikes = jam.limite_superlikes
                model.superlikes_usados = jam.superlikes_usados
                model.meta_votos_pular = jam.meta_votos_pular
                model.duracao_acumulada_segundos = jam.duracao_acumulada_segundos
                model.fonte_deck = jam.fonte_deck
                model.playlist_origem_id = jam.playlist_origem_id
                self.session.commit()
                self.session.refresh(model)
                return _to_jam_entity(model)

        model = JamModel(
            host_usuario_id=jam.host_usuario_id,
            nome_sala=jam.nome_sala,
            codigo_sala=jam.codigo_sala,
            is_ativa=jam.is_ativa,
            musica_atual_id=jam.musica_atual_id,
            duracao_minutos=jam.duracao_minutos,
            limite_superlikes=jam.limite_superlikes,
            superlikes_usados=jam.superlikes_usados,
            meta_votos_pular=jam.meta_votos_pular,
            duracao_acumulada_segundos=jam.duracao_acumulada_segundos,
            fonte_deck=jam.fonte_deck,
            playlist_origem_id=jam.playlist_origem_id,
        )
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return _to_jam_entity(model)

    def adicionar_musica_fila(
        self, jam_id: int, musica_id: int, pontos: int = 0
    ) -> JamFila:
        existente = (
            self.session.query(JamFilaModel)
            .filter(JamFilaModel.jam_id == jam_id, JamFilaModel.musica_id == musica_id)
            .first()
        )
        if existente:
            existente.pontos_voto += pontos
            self.session.commit()
            self.session.refresh(existente)
            return _to_jam_fila_entity(existente)

        model = JamFilaModel(jam_id=jam_id, musica_id=musica_id, pontos_voto=pontos)
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return _to_jam_fila_entity(model)

    def listar_fila(self, jam_id: int) -> list[JamFila]:
        models = (
            self.session.query(JamFilaModel)
            .filter(JamFilaModel.jam_id == jam_id)
            .order_by(JamFilaModel.pontos_voto.desc(), JamFilaModel.adicionado_em.asc())
            .all()
        )
        return [_to_jam_fila_entity(m) for m in models]

    def atualizar_voto_musica(
        self, jam_id: int, musica_id: int, delta_pontos: int
    ) -> JamFila | None:
        model = (
            self.session.query(JamFilaModel)
            .filter(JamFilaModel.jam_id == jam_id, JamFilaModel.musica_id == musica_id)
            .first()
        )
        if not model:
            return None
        model.pontos_voto += delta_pontos
        self.session.commit()
        self.session.refresh(model)
        return _to_jam_fila_entity(model)

    def remover_musica_fila(self, jam_id: int, musica_id: int) -> bool:
        model = (
            self.session.query(JamFilaModel)
            .filter(JamFilaModel.jam_id == jam_id, JamFilaModel.musica_id == musica_id)
            .first()
        )
        if not model:
            return False
        self.session.delete(model)
        self.session.commit()
        return True

    def adicionar_participante(self, jam_id: int, usuario_id: int) -> None:
        participante = (
            self.session.query(JamParticipanteModel)
            .filter_by(jam_id=jam_id, usuario_id=usuario_id)
            .first()
        )
        if participante:
            return
        self.session.add(JamParticipanteModel(jam_id=jam_id, usuario_id=usuario_id))
        self.session.commit()

    def eh_participante(self, jam_id: int, usuario_id: int) -> bool:
        return (
            self.session.query(JamParticipanteModel)
            .filter_by(jam_id=jam_id, usuario_id=usuario_id)
            .first()
            is not None
        )

    def registrar_voto_pular(self, jam_id: int, musica_id: int, usuario_id: int) -> int:
        voto = (
            self.session.query(JamVotoPularModel)
            .filter_by(jam_id=jam_id, musica_id=musica_id, usuario_id=usuario_id)
            .first()
        )
        if not voto:
            self.session.add(
                JamVotoPularModel(
                    jam_id=jam_id, musica_id=musica_id, usuario_id=usuario_id
                )
            )
            self.session.commit()
        return self.contar_votos_pular(jam_id, musica_id)

    def contar_votos_pular(self, jam_id: int, musica_id: int) -> int:
        return (
            self.session.query(JamVotoPularModel)
            .filter_by(jam_id=jam_id, musica_id=musica_id)
            .count()
        )

    def limpar_votos_pular(self, jam_id: int, musica_id: int) -> None:
        (
            self.session.query(JamVotoPularModel)
            .filter_by(jam_id=jam_id, musica_id=musica_id)
            .delete(synchronize_session=False)
        )
        self.session.commit()


class AvaliacaoRepository(AvaliacaoRepositoryPort):
    """Implementação do repositório de avaliações e comentários."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def buscar_por_id(self, avaliacao_id: int) -> AvaliacaoComentario | None:
        model = (
            self.session.query(AvaliacaoComentarioModel)
            .filter(AvaliacaoComentarioModel.avaliacao_id == avaliacao_id)
            .first()
        )
        return _to_avaliacao_entity(model) if model else None

    def buscar_por_usuario_e_musica(
        self, usuario_id: int, musica_id: int
    ) -> AvaliacaoComentario | None:
        model = (
            self.session.query(AvaliacaoComentarioModel)
            .filter_by(usuario_id=usuario_id, musica_id=musica_id)
            .first()
        )
        return _to_avaliacao_entity(model) if model else None

    def salvar(self, avaliacao: AvaliacaoComentario) -> AvaliacaoComentario:
        if avaliacao.avaliacao_id:
            model = (
                self.session.query(AvaliacaoComentarioModel)
                .filter(AvaliacaoComentarioModel.avaliacao_id == avaliacao.avaliacao_id)
                .first()
            )
            if model:
                model.nota = avaliacao.nota
                model.texto = avaliacao.texto
                model.likes_count = avaliacao.likes_count
                model.is_deleted = avaliacao.is_deleted
                self.session.commit()
                self.session.refresh(model)
                return _to_avaliacao_entity(model)

        model = AvaliacaoComentarioModel(
            usuario_id=avaliacao.usuario_id,
            musica_id=avaliacao.musica_id,
            nota=avaliacao.nota,
            texto=avaliacao.texto,
            likes_count=avaliacao.likes_count,
            is_deleted=avaliacao.is_deleted,
        )
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return _to_avaliacao_entity(model)

    def listar_por_musica(
        self, musica_id: int, limite: int = 50
    ) -> list[AvaliacaoComentario]:
        models = (
            self.session.query(AvaliacaoComentarioModel)
            .filter(
                AvaliacaoComentarioModel.musica_id == musica_id,
                AvaliacaoComentarioModel.is_deleted.is_(False),
            )
            .order_by(AvaliacaoComentarioModel.criado_em.desc())
            .limit(limite)
            .all()
        )
        return [_to_avaliacao_entity(m) for m in models]

    def listar_top_recentes(
        self, dias: int = 5, limite: int = 3
    ) -> list[AvaliacaoComentario]:
        limite_data = datetime.now(UTC) - timedelta(days=dias)
        models = (
            self.session.query(AvaliacaoComentarioModel)
            .filter(
                AvaliacaoComentarioModel.is_deleted.is_(False),
                AvaliacaoComentarioModel.criado_em >= limite_data,
            )
            .order_by(AvaliacaoComentarioModel.likes_count.desc())
            .limit(limite)
            .all()
        )
        return [_to_avaliacao_entity(m) for m in models]

    def excluir(self, avaliacao_id: int) -> bool:
        model = (
            self.session.query(AvaliacaoComentarioModel)
            .filter_by(avaliacao_id=avaliacao_id)
            .first()
        )
        if not model:
            return False
        self.session.delete(model)
        self.session.commit()
        return True

    def curtir(self, avaliacao_id: int, usuario_id: int) -> AvaliacaoComentario:
        model = (
            self.session.query(AvaliacaoComentarioModel)
            .filter_by(avaliacao_id=avaliacao_id)
            .first()
        )
        if not model:
            return None
        curtida = (
            self.session.query(AvaliacaoCurtidaModel)
            .filter_by(avaliacao_id=avaliacao_id, usuario_id=usuario_id)
            .first()
        )
        if not curtida:
            self.session.add(
                AvaliacaoCurtidaModel(avaliacao_id=avaliacao_id, usuario_id=usuario_id)
            )
            model.likes_count += 1
            self.session.commit()
            self.session.refresh(model)
        return _to_avaliacao_entity(model)
