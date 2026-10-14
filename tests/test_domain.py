"""Unit tests for domain entities and domain rules."""

from app.domain.entities import Interacao, Musica, Plano, Usuario


def test_plano_entity_creation():
    plano = Plano(plano_id=1, nome="Free", preco_mensal=0.0, max_perfis=1)
    assert plano.nome == "Free"
    assert plano.max_perfis == 1


def test_usuario_entity_creation():
    usuario = Usuario(
        usuario_id=1,
        email="user@example.com",
        senha_hash="hashed_pw",
        nome_exibicao="User One",
        idade=20,
        plano_id=1,
    )
    assert usuario.email == "user@example.com"
    assert usuario.is_admin is False
    assert usuario.titular_id is None


def test_musica_entity_creation():
    musica = Musica(
        musica_id=1,
        titulo="Bohemian Rhapsody",
        artista="Queen",
        duracao_segundos=354,
        genero="Rock",
        bloqueado_para_menores=False,
    )
    assert musica.titulo == "Bohemian Rhapsody"
    assert musica.is_deleted is False


def test_interacao_entity_creation():
    interacao = Interacao(
        interacao_id=1,
        usuario_id=1,
        musica_id=1,
        acao="curtida",
    )
    assert interacao.acao == "curtida"
