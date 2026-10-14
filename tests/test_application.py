"""Unit tests for Application Use Cases."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.application.auth_use_cases import AuthUseCases
from app.application.descoberta_use_cases import DescobertaUseCases
from app.application.perfil_use_cases import PerfilUseCases
from app.domain.exceptions import (
    BusinessRuleViolationError,
    DuplicateEntityError,
)
from app.infrastructure.database import Base
from app.infrastructure.repositories import (
    InteracaoRepository,
    MusicaRepository,
    PlanoRepository,
    UsuarioRepository,
)
from app.infrastructure.seed import run_seed


@pytest.fixture
def use_cases_fixture():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    session = TestingSessionLocal()
    run_seed(session)

    usuario_repo = UsuarioRepository(session)
    plano_repo = PlanoRepository(session)
    musica_repo = MusicaRepository(session)
    interacao_repo = InteracaoRepository(session)

    auth_uc = AuthUseCases(usuario_repo, plano_repo)
    descoberta_uc = DescobertaUseCases(usuario_repo, musica_repo, interacao_repo)
    perfil_uc = PerfilUseCases(usuario_repo, plano_repo, interacao_repo, musica_repo)

    return {
        "auth_uc": auth_uc,
        "descoberta_uc": descoberta_uc,
        "perfil_uc": perfil_uc,
        "usuario_repo": usuario_repo,
        "musica_repo": musica_repo,
        "plano_repo": plano_repo,
    }


def test_auth_cadastro_e_duplicidade(use_cases_fixture):
    auth_uc = use_cases_fixture["auth_uc"]
    user = auth_uc.cadastrar_usuario(
        email="test@user.com",
        senha="secretpassword",
        nome_exibicao="User Test",
        idade=20,
    )
    assert user.usuario_id is not None
    assert user.email == "test@user.com"

    # Duplicidade
    with pytest.raises(DuplicateEntityError):
        auth_uc.cadastrar_usuario(
            email="test@user.com",
            senha="otherpassword",
            nome_exibicao="User Clone",
            idade=20,
        )


def test_descoberta_trava_menor_de_idade(use_cases_fixture):
    auth_uc = use_cases_fixture["auth_uc"]
    descoberta_uc = use_cases_fixture["descoberta_uc"]

    menor = auth_uc.cadastrar_usuario(
        email="menor@ribbit.com",
        senha="secretpassword",
        nome_exibicao="Menor de Idade",
        idade=16,
    )

    # Obter músicas no swipe para o menor - nenhuma pode ter bloqueado_para_menores=True
    for _ in range(5):
        proxima = descoberta_uc.obter_proxima_musica_swipe(menor.usuario_id)
        if not proxima:
            break
        assert proxima.bloqueado_para_menores is False
        descoberta_uc.registrar_interacao_swipe(
            menor.usuario_id, proxima.musica_id, "curtida"
        )


def test_perfil_plano_familia_limite(use_cases_fixture):
    auth_uc = use_cases_fixture["auth_uc"]
    perfil_uc = use_cases_fixture["perfil_uc"]
    plano_repo = use_cases_fixture["plano_repo"]

    plano_familia = plano_repo.buscar_por_nome("Família")
    assert plano_familia is not None

    titular = auth_uc.cadastrar_usuario(
        email="titular@ribbit.com",
        senha="secretpassword",
        nome_exibicao="Titular Familia",
        idade=35,
        plano_id=plano_familia.plano_id,
    )

    # Criar e adicionar dependentes
    for i in range(plano_familia.max_perfis - 1):
        dep = auth_uc.cadastrar_usuario(
            email=f"dep{i}@ribbit.com",
            senha="secretpassword",
            nome_exibicao=f"Dependente {i}",
            idade=18,
        )
        perfil_uc.adicionar_membro_familia(titular.usuario_id, dep.usuario_id)

    # Tentativa de adicionar além do limite
    extra = auth_uc.cadastrar_usuario(
        email="extra@ribbit.com",
        senha="secretpassword",
        nome_exibicao="Extra",
        idade=18,
    )
    with pytest.raises(BusinessRuleViolationError):
        perfil_uc.adicionar_membro_familia(titular.usuario_id, extra.usuario_id)
