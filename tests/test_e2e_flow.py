"""End-to-end tests for authentication, playlists, family, Jam, and administration."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.application.auth_use_cases import hash_password
from app.infrastructure.database import Base, get_db
from app.infrastructure.db_models import MusicaModel
from app.infrastructure.seed import run_seed
from app.main import app

test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
ADMIN_EMAIL = "admin@ribbit.example.com"
ADMIN_PASSWORD = "RibbitLocal2026!"


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
    run_seed(session, hash_password)
    session.close()
    app.dependency_overrides[get_db] = override_get_db
    yield
    Base.metadata.drop_all(bind=test_engine)
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    return TestClient(app)


def _cadastrar(client: TestClient, email: str, data_nascimento: str, plano_id: int):
    resposta = client.post(
        "/api/auth/cadastrar",
        json={
            "email": email,
            "senha": "password123",
            "nome_exibicao": "Ribbit Test",
            "data_nascimento": data_nascimento,
            "plano_id": plano_id,
        },
    )
    assert resposta.status_code == 201, resposta.text
    login = client.post(
        "/api/auth/login", json={"email": email, "senha": "password123"}
    )
    assert login.status_code == 200, login.text
    return resposta.json(), {"Authorization": f"Bearer {login.json()['access_token']}"}


def test_auth_blocked_minor_and_bearer_identity(client):
    planos = client.get("/api/planos").json()
    free_id = next(plano["plano_id"] for plano in planos if plano["nome"] == "Free")

    cadastro = client.post(
        "/api/auth/cadastrar",
        json={
            "email": "minor-direct@ribbit.com",
            "senha": "password123",
            "nome_exibicao": "Minor",
            "data_nascimento": "2012-01-01",
        },
    )
    assert cadastro.status_code == 400

    user, headers = _cadastrar(client, "adult@ribbit.com", "1990-01-01", free_id)
    assert client.get("/api/perfil/me").status_code == 401
    profile = client.get("/api/perfil/me?usuario_id=999999", headers=headers)
    assert profile.status_code == 200
    assert profile.json()["usuario"]["usuario_id"] == user["usuario_id"]


def test_playlist_deck_and_owner_only_writes(client):
    planos = client.get("/api/planos").json()
    individual_id = next(
        plano["plano_id"] for plano in planos if plano["nome"] == "Individual"
    )
    _, headers = _cadastrar(
        client, "playlist-owner@ribbit.com", "1988-04-05", individual_id
    )
    deck = client.post(
        "/api/playlists/deck",
        headers=headers,
        json={"nome": "Pop curta", "duracao_minutos": 5, "genero": "Pop"},
    )
    assert deck.status_code == 201, deck.text
    playlist_id = deck.json()["playlist_id"]
    assert deck.json()["musicas"] == []
    first_page = client.get(
        f"/api/playlists/{playlist_id}/deck?limite=20", headers=headers
    )
    assert first_page.status_code == 200
    assert first_page.json()["items"]
    assert all(track["duracao_segundos"] <= 300 for track in first_page.json()["items"])

    track = first_page.json()["items"][0]
    added = client.post(
        f"/api/playlists/{playlist_id}/swipe-add",
        headers=headers,
        json={"musica_id": track["musica_id"], "acao": "superlike"},
    )
    assert added.status_code == 200, added.text
    remaining_deck = client.get(f"/api/playlists/{playlist_id}/deck", headers=headers)
    assert remaining_deck.status_code == 200
    assert track["musica_id"] not in {
        candidate["musica_id"] for candidate in remaining_deck.json()["items"]
    }
    other_suggestion = next(
        candidate
        for candidate in first_page.json()["items"]
        if candidate["musica_id"] != track["musica_id"]
    )
    over_duration = client.post(
        f"/api/playlists/{playlist_id}/swipe-add",
        headers=headers,
        json={"musica_id": other_suggestion["musica_id"], "acao": "curtida"},
    )
    assert over_duration.status_code == 400
    detail = client.get(f"/api/playlists/{playlist_id}", headers=headers)
    assert detail.status_code == 200
    assert detail.json()["duracao_total_segundos"] == track["duracao_segundos"]

    other, other_headers = _cadastrar(
        client, "playlist-other@ribbit.com", "1985-03-02", individual_id
    )
    assert other["usuario_id"] != detail.json()["usuario_id"]
    denied = client.delete(f"/api/playlists/{playlist_id}", headers=other_headers)
    assert denied.status_code == 403


def test_family_minor_is_filtered_and_jam_votes_advance_automatically(client):
    planos = client.get("/api/planos").json()
    family_id = next(
        plano["plano_id"] for plano in planos if plano["nome"] == "Família"
    )
    _, host_headers = _cadastrar(
        client, "family-owner@ribbit.com", "1980-05-01", family_id
    )
    member = client.post(
        "/api/perfil/familia/membros",
        headers=host_headers,
        json={
            "email": "family-child@ribbit.com",
            "senha": "password123",
            "nome_exibicao": "Child Profile",
            "data_nascimento": "2012-02-01",
        },
    )
    assert member.status_code == 200, member.text
    child_login = client.post(
        "/api/auth/login",
        json={"email": "family-child@ribbit.com", "senha": "password123"},
    )
    child_headers = {"Authorization": f"Bearer {child_login.json()['access_token']}"}

    room = client.post(
        "/api/jams",
        headers=host_headers,
        json={
            "nome_sala": "Family Jam",
            "duracao_minutos": 60,
            "limite_superlikes": 1,
            "meta_votos_pular": 2,
        },
    )
    assert room.status_code == 201, room.text
    jam = room.json()
    joined = client.post(
        "/api/jams/entrar",
        headers=child_headers,
        json={"codigo_sala": jam["codigo_sala"]},
    )
    assert joined.status_code == 200
    child_deck = client.get(
        f"/api/jams/{jam['jam_id']}/deck-adicionar", headers=child_headers
    )
    assert child_deck.status_code == 200
    assert all(track["titulo"] != "Rap God" for track in child_deck.json()["items"])

    with TestingSessionLocal() as session:
        musicas = {
            row.titulo: row.musica_id
            for row in session.query(MusicaModel)
            .filter(MusicaModel.titulo.in_(["Shape of You", "Blinding Lights"]))
            .all()
        }
    first = musicas["Shape of You"]
    second = musicas["Blinding Lights"]
    first_add = client.post(
        f"/api/jams/{jam['jam_id']}/interagir-deck",
        headers=host_headers,
        json={"musica_id": first, "acao": "like"},
    )
    assert first_add.status_code == 200, first_add.text
    second_add = client.post(
        f"/api/jams/{jam['jam_id']}/interagir-deck",
        headers=host_headers,
        json={"musica_id": second, "acao": "superlike"},
    )
    assert second_add.status_code == 200, second_add.text
    over_limit = client.post(
        f"/api/jams/{jam['jam_id']}/interagir-deck",
        headers=host_headers,
        json={"musica_id": first, "acao": "superlike"},
    )
    assert over_limit.status_code == 400

    first_vote = client.post(
        f"/api/jams/{jam['jam_id']}/votar-pular",
        headers=host_headers,
        json={},
    )
    assert first_vote.status_code == 200, first_vote.text
    repeated_vote = client.post(
        f"/api/jams/{jam['jam_id']}/votar-pular",
        headers=host_headers,
        json={},
    )
    assert repeated_vote.json()["votos"] == 1
    second_vote = client.post(
        f"/api/jams/{jam['jam_id']}/votar-pular",
        headers=child_headers,
        json={},
    )
    assert second_vote.status_code == 200
    assert second_vote.json()["avancou"] is True
    state = client.get(f"/api/jams/{jam['jam_id']}/estado", headers=host_headers)
    assert state.json()["jam"]["musica_atual_id"] == second


def test_rejected_tracks_are_skipped_and_playlist_and_jam_decks_are_large(client):
    plans = client.get("/api/planos").json()
    individual_id = next(
        plan["plano_id"] for plan in plans if plan["nome"] == "Individual"
    )
    _, headers = _cadastrar(
        client, "large-deck-user@ribbit.com", "1991-06-07", individual_id
    )

    with TestingSessionLocal() as session:
        rejected = (
            session.query(MusicaModel)
            .filter(MusicaModel.titulo == "Blinding Lights")
            .first()
        )
        assert rejected is not None
        rejected_id = rejected.musica_id
        session.add_all(
            [
                MusicaModel(
                    titulo=f"Deck Track {index}",
                    artista="Ribbit Test",
                    duracao_segundos=180,
                    genero="Test",
                    bloqueado_para_menores=False,
                    is_deleted=False,
                )
                for index in range(60)
            ]
        )
        session.commit()

    rejected_response = client.post(
        "/api/descoberta/interagir",
        headers=headers,
        json={"musica_id": rejected_id, "acao": "rejeitada"},
    )
    assert rejected_response.status_code == 200, rejected_response.text

    playlist = client.post(
        "/api/playlists/deck",
        headers=headers,
        json={"nome": "Alternativas"},
    )
    assert playlist.status_code == 201, playlist.text
    playlist_id = playlist.json()["playlist_id"]
    playlist_suggestions = client.get(
        f"/api/playlists/{playlist_id}/deck?limite=20", headers=headers
    )
    assert playlist_suggestions.status_code == 200
    playlist_ids = {
        track["musica_id"] for track in playlist_suggestions.json()["items"]
    }
    assert rejected_id not in playlist_ids
    assert len(playlist_ids) == 20
    assert playlist_suggestions.json()["has_more"] is True
    next_playlist_page = client.get(
        f"/api/playlists/{playlist_id}/deck?limite=20"
        f"&cursor_id={playlist_suggestions.json()['next_cursor']}",
        headers=headers,
    )
    assert next_playlist_page.status_code == 200
    next_playlist_ids = {
        track["musica_id"] for track in next_playlist_page.json()["items"]
    }
    assert len(next_playlist_ids) == 20
    assert playlist_ids.isdisjoint(next_playlist_ids)

    jam = client.post(
        "/api/jams",
        headers=headers,
        json={"nome_sala": "Alternativas", "duracao_minutos": 600},
    )
    assert jam.status_code == 201, jam.text
    jam_suggestions = client.get(
        f"/api/jams/{jam.json()['jam_id']}/deck-adicionar?limite=20",
        headers=headers,
    )
    assert jam_suggestions.status_code == 200
    jam_ids = {track["musica_id"] for track in jam_suggestions.json()["items"]}
    assert rejected_id not in jam_ids
    assert len(jam_ids) == 20
    assert jam_suggestions.json()["has_more"] is True
    next_jam_page = client.get(
        f"/api/jams/{jam.json()['jam_id']}/deck-adicionar?limite=20"
        f"&cursor_id={jam_suggestions.json()['next_cursor']}",
        headers=headers,
    )
    assert next_jam_page.status_code == 200
    next_jam_ids = {track["musica_id"] for track in next_jam_page.json()["items"]}
    assert len(next_jam_ids) == 20
    assert jam_ids.isdisjoint(next_jam_ids)


def test_blocked_genre_does_not_hide_or_prevent_music_and_review_actions(client):
    plans = client.get("/api/planos").json()
    individual_id = next(
        plan["plano_id"] for plan in plans if plan["nome"] == "Individual"
    )
    _, headers = _cadastrar(
        client, "blocked-genre-user@ribbit.com", "1992-09-10", individual_id
    )
    blocked = client.put(
        "/api/perfil/generos-bloqueados",
        headers=headers,
        json={"generos_bloqueados": ["Rock"]},
    )
    assert blocked.status_code == 200, blocked.text

    search = client.get(
        "/api/musicas/buscar?genero=Rock",
        headers=headers,
    )
    assert search.status_code == 200
    queen = next(
        track for track in search.json() if track["titulo"] == "Bohemian Rhapsody"
    )

    favorite = client.post(
        f"/api/reviews/{queen['musica_id']}/curtir-busca",
        headers=headers,
        json={},
    )
    assert favorite.status_code == 200, favorite.text
    review = client.post(
        "/api/reviews",
        headers=headers,
        json={
            "musica_id": queen["musica_id"],
            "nota": 5,
            "texto": "Great song",
        },
    )
    assert review.status_code == 201, review.text


def test_admin_seed_uses_common_login_and_admin_role(client):
    login = client.post(
        "/api/auth/login",
        json={"email": ADMIN_EMAIL, "senha": ADMIN_PASSWORD},
    )
    assert login.status_code == 200, login.text
    token_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    assert client.get("/api/admin/dashboard", headers=token_headers).status_code == 200
    assert client.get("/api/admin/dashboard").status_code == 401
