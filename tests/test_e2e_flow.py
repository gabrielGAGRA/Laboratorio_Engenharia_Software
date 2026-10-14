"""End-to-End integration test covering the primary user flow of Ribbit V0."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.infrastructure.database import Base, get_db
from app.infrastructure.db_models import MusicaModel, PlanoModel, UsuarioModel
from app.infrastructure.seed import run_seed
from app.main import app

# In-memory database for isolated E2E testing
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    run_seed(session)
    session.close()
    app.dependency_overrides[get_db] = override_get_db
    yield
    Base.metadata.drop_all(bind=test_engine)
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    return TestClient(app)


def test_fluxo_principal_e2e(client):
    """Testa o fluxo principal ponta a ponta:
    1. Cadastro / Login
    2. Descoberta / Swipe
    3. Criação e Leitura de Playlists
    4. Perfil e Histórico
    """
    # ----------------------------------------------------
    # PASSO 1: CADASTRO / LOGIN
    # ----------------------------------------------------
    # Consulta planos disponíveis para selecionar o Individual
    resp_planos = client.get("/api/planos")
    assert resp_planos.status_code == 200
    planos = resp_planos.json()
    assert len(planos) >= 3
    plano_individual = next(p for p in planos if p["nome"] == "Individual")

    # Cadastro
    cadastro_payload = {
        "email": "crazyfrog@ribbit.com",
        "senha": "password123",
        "nome_exibicao": "Crazy Frog",
        "idade": 22,
        "plano_id": plano_individual["plano_id"],
    }
    resp_cadastro = client.post("/api/auth/cadastrar", json=cadastro_payload)
    assert resp_cadastro.status_code == 201
    usuario = resp_cadastro.json()
    usuario_id = usuario["usuario_id"]
    assert usuario["email"] == "crazyfrog@ribbit.com"
    assert usuario["plano_id"] == plano_individual["plano_id"]

    # Login
    login_payload = {
        "email": "crazyfrog@ribbit.com",
        "senha": "password123",
    }
    resp_login = client.post("/api/auth/login", json=login_payload)
    assert resp_login.status_code == 200
    assert resp_login.json()["usuario_id"] == usuario_id

    # ----------------------------------------------------
    # PASSO 2: DESCOBERTA / SWIPE
    # ----------------------------------------------------
    # Recebe primeira faixa para descoberta
    resp_proxima1 = client.get(f"/api/descoberta/proxima?usuario_id={usuario_id}")
    assert resp_proxima1.status_code == 200
    musica1 = resp_proxima1.json()
    assert musica1 is not None
    musica1_id = musica1["musica_id"]

    # Registra swipe 'curtida' na primeira música
    resp_swipe1 = client.post(
        "/api/descoberta/interagir",
        json={
            "usuario_id": usuario_id,
            "musica_id": musica1_id,
            "acao": "curtida",
        },
    )
    assert resp_swipe1.status_code == 200
    assert resp_swipe1.json()["acao"] == "curtida"

    # Próxima faixa de descoberta não pode ser a música já interagida
    resp_proxima2 = client.get(f"/api/descoberta/proxima?usuario_id={usuario_id}")
    assert resp_proxima2.status_code == 200
    musica2 = resp_proxima2.json()
    assert musica2 is not None
    musica2_id = musica2["musica_id"]
    assert musica2_id != musica1_id

    # Registra swipe 'amada' na segunda música
    resp_swipe2 = client.post(
        "/api/descoberta/interagir",
        json={
            "usuario_id": usuario_id,
            "musica_id": musica2_id,
            "acao": "amada",
        },
    )
    assert resp_swipe2.status_code == 200
    assert resp_swipe2.json()["acao"] == "amada"

    # ----------------------------------------------------
    # PASSO 3: CRIAÇÃO E LEITURA DE PLAYLISTS
    # ----------------------------------------------------
    # Cria deck de playlist por parâmetros
    deck_payload = {
        "usuario_id": usuario_id,
        "nome": "Minha Vibe Matinal",
        "duracao_minutos": 10,
        "genero": "Pop",
        "descricao": "Playlist gerada no Ribbit",
    }
    resp_deck = client.post("/api/playlists/deck", json=deck_payload)
    assert resp_deck.status_code == 201
    playlist_criada = resp_deck.json()
    playlist_id = playlist_criada["playlist_id"]
    assert playlist_criada["nome"] == "Minha Vibe Matinal"

    # Adiciona uma nova música na playlist via swipe
    resp_add = client.post(
        f"/api/playlists/{playlist_id}/swipe-add?usuario_id={usuario_id}",
        json={"musica_id": musica1_id},
    )
    assert resp_add.status_code == 200
    assert resp_add.json()["sucesso"] is True

    # Consulta a biblioteca de playlists do usuário
    resp_biblioteca = client.get(f"/api/playlists?usuario_id={usuario_id}")
    assert resp_biblioteca.status_code == 200
    playlists_usuario = resp_biblioteca.json()
    assert len(playlists_usuario) >= 1
    assert any(p["playlist_id"] == playlist_id for p in playlists_usuario)

    # ----------------------------------------------------
    # PASSO 4: PERFIL E HISTÓRICO
    # ----------------------------------------------------
    # Consulta dados do perfil
    resp_perfil = client.get(f"/api/perfil/me?usuario_id={usuario_id}")
    assert resp_perfil.status_code == 200
    perfil_dados = resp_perfil.json()
    assert perfil_dados["usuario"]["email"] == "crazyfrog@ribbit.com"
    assert perfil_dados["plano"]["nome"] == "Individual"

    # Consulta histórico de interações (curtidas e salvas)
    resp_historico = client.get(f"/api/perfil/historico?usuario_id={usuario_id}")
    assert resp_historico.status_code == 200
    historico = resp_historico.json()
    assert len(historico) >= 2
    acoes = [item["acao"] for item in historico]
    assert "curtida" in acoes
    assert "amada" in acoes


def test_admin_atualiza_restricao_de_menores(client):
    db = TestingSessionLocal()
    plano = db.query(PlanoModel).filter(PlanoModel.nome == "Free").first()
    musica = db.query(MusicaModel).filter(MusicaModel.titulo == "Shape of You").first()
    assert plano is not None
    assert musica is not None

    admin = UsuarioModel(
        email="admin-moderacao@ribbit.com",
        senha_hash="nao-utilizado-no-teste",
        nome_exibicao="Admin",
        idade=30,
        plano_id=plano.plano_id,
        is_admin=True,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    admin_id = admin.usuario_id
    musica_id = musica.musica_id
    db.close()

    bloqueio = client.put(
        f"/api/admin/musicas/{musica_id}/restricao-menores",
        headers={"X-Admin-Id": str(admin_id)},
        json={"bloqueado_para_menores": True},
    )
    assert bloqueio.status_code == 200
    assert bloqueio.json() == {
        "musica_id": musica_id,
        "bloqueado_para_menores": True,
    }

    desbloqueio = client.put(
        f"/api/admin/musicas/{musica_id}/restricao-menores",
        headers={"X-Admin-Id": str(admin_id)},
        json={"bloqueado_para_menores": False},
    )
    assert desbloqueio.status_code == 200
    assert desbloqueio.json()["bloqueado_para_menores"] is False


def test_restricao_etaria_em_busca_playlist_e_jam(client):
    db = TestingSessionLocal()
    plano = db.query(PlanoModel).filter(PlanoModel.nome == "Free").first()
    musica_restrita = (
        db.query(MusicaModel).filter(MusicaModel.titulo == "Rap God").first()
    )
    assert plano is not None
    assert musica_restrita is not None
    musica_restrita.bloqueado_para_menores = True

    adulto = UsuarioModel(
        email="adulto-jam-restricao@ribbit.com",
        senha_hash="nao-utilizado-no-teste",
        nome_exibicao="Adulto",
        idade=30,
        plano_id=plano.plano_id,
    )
    menor = UsuarioModel(
        email="menor-restricao@ribbit.com",
        senha_hash="nao-utilizado-no-teste",
        nome_exibicao="Menor",
        idade=16,
        plano_id=plano.plano_id,
    )
    db.add(adulto)
    db.add(menor)
    db.commit()
    db.refresh(adulto)
    db.refresh(menor)
    usuario_id = menor.usuario_id
    adulto_id = adulto.usuario_id
    musica_id = musica_restrita.musica_id
    db.close()

    busca = client.get(f"/api/musicas/buscar?usuario_id={usuario_id}&termo=Rap%20God")
    assert busca.status_code == 200
    assert all(musica["musica_id"] != musica_id for musica in busca.json())

    deck = client.post(
        "/api/playlists/deck",
        json={"usuario_id": usuario_id, "nome": "Playlist do menor"},
    )
    assert deck.status_code == 201
    playlist_id = deck.json()["playlist_id"]

    adicionar = client.post(
        f"/api/playlists/{playlist_id}/swipe-add?usuario_id={usuario_id}",
        json={"musica_id": musica_id},
    )
    assert adicionar.status_code == 400
    assert "bloqueada para usuários menores" in adicionar.json()["mensagem"]

    jam = client.post(
        "/api/jams",
        json={"host_usuario_id": adulto_id, "nome_sala": "Jam com restrição"},
    )
    assert jam.status_code == 201

    adulto_vota = client.post(
        f"/api/jams/{jam.json()['jam_id']}/votar",
        json={"usuario_id": adulto_id, "musica_id": musica_id},
    )
    assert adulto_vota.status_code == 200

    votar = client.post(
        f"/api/jams/{jam.json()['jam_id']}/votar",
        json={"usuario_id": usuario_id, "musica_id": musica_id},
    )
    assert votar.status_code == 400
    assert "bloqueada para usuários menores" in votar.json()["mensagem"]

    estado = client.get(
        f"/api/jams/{jam.json()['jam_id']}/estado?usuario_id={usuario_id}"
    )
    assert estado.status_code == 200
    assert estado.json()["fila"] == []

    avancar = client.post(
        f"/api/jams/{jam.json()['jam_id']}/avancar?solicitante_usuario_id={adulto_id}"
    )
    assert avancar.status_code == 200

    estado_atual = client.get(
        f"/api/jams/{jam.json()['jam_id']}/estado?usuario_id={usuario_id}"
    )
    assert estado_atual.status_code == 200
    assert estado_atual.json()["musica_atual"] is None
    assert estado_atual.json()["jam"]["musica_atual_id"] is None

    db = TestingSessionLocal()
    musica_restrita = (
        db.query(MusicaModel).filter(MusicaModel.musica_id == musica_id).first()
    )
    assert musica_restrita is not None
    musica_restrita.bloqueado_para_menores = False
    musica_restrita.is_deleted = True
    db.commit()
    db.close()

    estado_excluida = client.get(
        f"/api/jams/{jam.json()['jam_id']}/estado?usuario_id={usuario_id}"
    )
    assert estado_excluida.status_code == 200
    assert estado_excluida.json()["musica_atual"] is None
