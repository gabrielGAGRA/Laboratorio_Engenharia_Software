"""Tests for infrastructure database models, repositories, and seed."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.domain.entities import Interacao, Usuario
from app.infrastructure.database import Base
from app.infrastructure.repositories import (
    InteracaoRepository,
    MusicaRepository,
    PlanoRepository,
    UsuarioRepository,
)
from app.infrastructure.seed import run_seed


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    session = TestingSessionLocal()
    run_seed(session)
    yield session
    session.close()


def test_seed_populates_planos_and_musicas(db_session):
    plano_repo = PlanoRepository(db_session)
    planos = plano_repo.listar_todos()
    assert len(planos) == 3
    nomes = {p.nome for p in planos}
    assert "Free" in nomes
    assert "Individual" in nomes
    assert "Família" in nomes

    musica_repo = MusicaRepository(db_session)
    musicas = musica_repo.listar_ativas()
    assert len(musicas) >= 5


def test_usuario_and_interacao_persistence(db_session):
    usuario_repo = UsuarioRepository(db_session)
    plano_repo = PlanoRepository(db_session)
    free_plano = plano_repo.buscar_por_nome("Free")
    assert free_plano is not None

    usuario = usuario_repo.salvar(
        Usuario(
            usuario_id=None,
            email="test@ribbit.com",
            senha_hash="xyz123",
            nome_exibicao="Test User",
            idade=25,
            plano_id=free_plano.plano_id,
        )
    )
    assert usuario.usuario_id is not None

    musica_repo = MusicaRepository(db_session)
    musica = musica_repo.listar_ativas()[0]

    interacao_repo = InteracaoRepository(db_session)
    interacao = interacao_repo.salvar(
        Interacao(
            interacao_id=None,
            usuario_id=usuario.usuario_id,
            musica_id=musica.musica_id,
            acao="curtida",
        )
    )
    assert interacao.interacao_id is not None
    assert interacao_repo.listar_ids_musicas_interagidas(usuario.usuario_id) == [
        musica.musica_id
    ]
