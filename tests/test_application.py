"""Unit tests for Application Use Cases."""

from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.application.admin_use_cases import AdminUseCases
from app.application.auth_use_cases import AuthUseCases
from app.application.descoberta_use_cases import DescobertaUseCases
from app.application.exceptions import (
    BusinessRuleViolationError,
    DuplicateEntityError,
    ForbiddenError,
)
from app.application.jam_use_cases import JamUseCases
from app.application.perfil_use_cases import PerfilUseCases
from app.application.playlist_use_cases import PlaylistUseCases
from app.application.review_use_cases import ReviewUseCases
from app.domain.entities import Interacao, Musica
from app.infrastructure.apis_externas import ExternalMusicServiceAdapter
from app.infrastructure.database import Base
from app.infrastructure.repositories import (
    AvaliacaoRepository,
    InteracaoRepository,
    JamRepository,
    MusicaRepository,
    PlanoRepository,
    PlaylistRepository,
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
    playlist_repo = PlaylistRepository(session)
    avaliacao_repo = AvaliacaoRepository(session)
    jam_repo = JamRepository(session)
    external_service = ExternalMusicServiceAdapter()

    auth_uc = AuthUseCases(usuario_repo, plano_repo)
    descoberta_uc = DescobertaUseCases(usuario_repo, musica_repo, interacao_repo)
    perfil_uc = PerfilUseCases(usuario_repo, plano_repo, interacao_repo, musica_repo)
    playlist_uc = PlaylistUseCases(
        usuario_repo, musica_repo, playlist_repo, external_service, interacao_repo
    )
    jam_uc = JamUseCases(
        jam_repo, usuario_repo, musica_repo, interacao_repo, playlist_repo
    )
    review_uc = ReviewUseCases(
        musica_repo,
        avaliacao_repo,
        usuario_repo,
        interacao_repo,
        playlist_repo,
        external_service,
    )
    admin_uc = AdminUseCases(usuario_repo, plano_repo, musica_repo, avaliacao_repo)

    return {
        "auth_uc": auth_uc,
        "descoberta_uc": descoberta_uc,
        "perfil_uc": perfil_uc,
        "playlist_uc": playlist_uc,
        "jam_uc": jam_uc,
        "review_uc": review_uc,
        "admin_uc": admin_uc,
        "usuario_repo": usuario_repo,
        "musica_repo": musica_repo,
        "plano_repo": plano_repo,
        "interacao_repo": interacao_repo,
        "playlist_repo": playlist_repo,
        "avaliacao_repo": avaliacao_repo,
        "session": session,
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

    plano_familia = use_cases_fixture["plano_repo"].buscar_por_nome("Família")
    titular = auth_uc.cadastrar_usuario(
        email="titular-menor@ribbit.com",
        senha="secretpassword",
        nome_exibicao="Titular",
        idade=35,
        plano_id=plano_familia.plano_id,
    )
    menor = use_cases_fixture["perfil_uc"].adicionar_membro_familia(
        titular_id=titular.usuario_id,
        email="menor@ribbit.com",
        senha="secretpassword",
        nome_exibicao="Menor de Idade",
        data_nascimento=date(2010, 1, 1),
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

    # Adicionar dependentes, inclusive menores, diretamente pelo titular
    for i in range(plano_familia.max_perfis - 1):
        perfil_uc.adicionar_membro_familia(
            titular_id=titular.usuario_id,
            email=f"dep{i}@ribbit.com",
            senha="secretpassword",
            nome_exibicao=f"Dependente {i}",
            data_nascimento=date(2012, 1, 1),
        )

    # Tentativa de exceder limite da Família
    with pytest.raises(BusinessRuleViolationError):
        perfil_uc.adicionar_membro_familia(
            titular_id=titular.usuario_id,
            email="extra@ribbit.com",
            senha="secretpassword",
            nome_exibicao="Extra",
            data_nascimento=date(2010, 1, 1),
        )


def test_review_validation_duplicate_authorization_and_unique_likes(
    use_cases_fixture,
):
    auth_uc = use_cases_fixture["auth_uc"]
    review_uc = use_cases_fixture["review_uc"]
    plano_id = use_cases_fixture["plano_repo"].buscar_por_nome("Individual").plano_id
    author = auth_uc.cadastrar_usuario(
        "review-author@ribbit.com", "secretpassword", "Review Author", 28, plano_id
    )
    reader = auth_uc.cadastrar_usuario(
        "review-reader@ribbit.com", "secretpassword", "Review Reader", 30, plano_id
    )
    song = next(
        item
        for item in use_cases_fixture["musica_repo"].listar_ativas()
        if item.titulo == "Bohemian Rhapsody"
    )

    with pytest.raises(BusinessRuleViolationError, match="entre 1 e 5"):
        review_uc.publicar_review(author.usuario_id, song.musica_id, 0, "invalid")
    with pytest.raises(BusinessRuleViolationError, match="entre 1 e 5"):
        review_uc.publicar_review(author.usuario_id, song.musica_id, 6, "invalid")

    review = review_uc.publicar_review(
        author.usuario_id, song.musica_id, 5, "  Great song  "
    )
    assert review.texto == "Great song"
    with pytest.raises(DuplicateEntityError):
        review_uc.publicar_review(author.usuario_id, song.musica_id, 4, "duplicate")

    liked = review_uc.dar_like_comentario(review.avaliacao_id, reader.usuario_id)
    assert liked.likes_count == 1
    assert (
        review_uc.dar_like_comentario(
            review.avaliacao_id, reader.usuario_id
        ).likes_count
        == 1
    )
    with pytest.raises(ForbiddenError):
        review_uc.excluir_review(review.avaliacao_id, reader.usuario_id)
    assert review_uc.excluir_review(review.avaliacao_id, author.usuario_id) is True


def test_reviews_allow_blocked_genres_but_keep_minor_content_filter(
    use_cases_fixture,
):
    auth_uc = use_cases_fixture["auth_uc"]
    perfil_uc = use_cases_fixture["perfil_uc"]
    review_uc = use_cases_fixture["review_uc"]
    usuario_repo = use_cases_fixture["usuario_repo"]
    plano_repo = use_cases_fixture["plano_repo"]
    individual = plano_repo.buscar_por_nome("Individual")
    family = plano_repo.buscar_por_nome("Família")
    adult = auth_uc.cadastrar_usuario(
        "genre-blocked@ribbit.com",
        "secretpassword",
        "Genre Blocked",
        25,
        individual.plano_id,
    )
    adult.generos_bloqueados = "rock"
    usuario_repo.salvar(adult)

    found = review_uc.buscar_musicas_por_filtro(adult.usuario_id, genero="Rock")
    queen = next(song for song in found if song.titulo == "Bohemian Rhapsody")
    assert review_uc.salvar_musica_curti_busca(adult.usuario_id, queen.musica_id)
    assert review_uc.publicar_review(adult.usuario_id, queen.musica_id, 5)

    titular = auth_uc.cadastrar_usuario(
        "minor-family@ribbit.com",
        "secretpassword",
        "Minor Family",
        40,
        family.plano_id,
    )
    child = perfil_uc.adicionar_membro_familia(
        titular.usuario_id,
        "minor-review@ribbit.com",
        "secretpassword",
        "Minor",
        date.today().replace(year=date.today().year - 14),
    )
    explicit_search = review_uc.buscar_musicas_por_filtro(
        child.usuario_id, termo="Rap God"
    )
    assert all(song.titulo != "Rap God" for song in explicit_search)

    explicit_song = next(
        song
        for song in use_cases_fixture["musica_repo"].listar_ativas()
        if song.titulo == "Rap God"
    )
    with pytest.raises(BusinessRuleViolationError, match="menores de idade"):
        review_uc.salvar_musica_curti_busca(child.usuario_id, explicit_song.musica_id)


def test_admin_audience_report_and_revenue_exclude_family_dependents(
    use_cases_fixture,
):
    auth_uc = use_cases_fixture["auth_uc"]
    perfil_uc = use_cases_fixture["perfil_uc"]
    admin_uc = use_cases_fixture["admin_uc"]
    usuario_repo = use_cases_fixture["usuario_repo"]
    musica_repo = use_cases_fixture["musica_repo"]
    plano_repo = use_cases_fixture["plano_repo"]

    family = plano_repo.buscar_por_nome("Família")
    individual = plano_repo.buscar_por_nome("Individual")
    holder = auth_uc.cadastrar_usuario(
        "dashboard-holder@ribbit.com",
        "secretpassword",
        "Dashboard Holder",
        40,
        family.plano_id,
    )
    dependent = perfil_uc.adicionar_membro_familia(
        holder.usuario_id,
        "dashboard-dependent@ribbit.com",
        "secretpassword",
        "Dashboard Dependent",
        date.today().replace(year=date.today().year - 12),
    )
    individual_user = auth_uc.cadastrar_usuario(
        "dashboard-individual@ribbit.com",
        "secretpassword",
        "Dashboard Individual",
        30,
        individual.plano_id,
    )
    holder.generos_bloqueados = "rock, pop"
    dependent.generos_bloqueados = "rock"
    usuario_repo.salvar(holder)
    usuario_repo.salvar(dependent)

    total_songs = musica_repo.contar_todas()
    deleted = musica_repo.listar_ativas()[0]
    admin_uc.bloquear_musica(deleted.musica_id, True)
    report = admin_uc.obter_relatorio_audiencia()
    assert report["total_usuarios"] == 3
    assert report["total_musicas"] == total_songs
    assert report["musicas_ativas"] == total_songs - 1
    assert report["generos_bloqueados"] == {"rock": 2, "pop": 1}

    dashboard = admin_uc.obter_dashboard_executivo()
    assert dashboard["total_usuarios"] == 3
    assert dashboard["receita_liquida_estimada"] == 42.8
    assert dashboard["usuarios_por_plano"] == {
        "Free": 0,
        "Individual": 1,
        "Família": 2,
    }
    assert dashboard["receita_por_plano"] == {
        "Free": 0.0,
        "Individual": 14.9,
        "Família": 27.9,
    }
    assert individual_user.titular_id is None


def test_playlist_and_jam_decks_filter_genre_rejections_and_age(
    use_cases_fixture,
):
    auth_uc = use_cases_fixture["auth_uc"]
    perfil_uc = use_cases_fixture["perfil_uc"]
    usuario_repo = use_cases_fixture["usuario_repo"]
    musica_repo = use_cases_fixture["musica_repo"]
    interacao_repo = use_cases_fixture["interacao_repo"]
    playlist_uc = use_cases_fixture["playlist_uc"]
    jam_uc = use_cases_fixture["jam_uc"]
    plano_repo = use_cases_fixture["plano_repo"]

    individual = plano_repo.buscar_por_nome("Individual")
    adult = auth_uc.cadastrar_usuario(
        "filtered-deck@ribbit.com",
        "secretpassword",
        "Filtered Deck",
        25,
        individual.plano_id,
    )
    adult.generos_bloqueados = "rock"
    usuario_repo.salvar(adult)
    songs = musica_repo.listar_ativas()
    rejected_song = next(song for song in songs if song.titulo == "Shape of You")
    interacao_repo.salvar(
        Interacao(
            interacao_id=None,
            usuario_id=adult.usuario_id,
            musica_id=rejected_song.musica_id,
            acao="rejeitada",
        )
    )
    for index in range(25):
        musica_repo.salvar(
            Musica(
                musica_id=None,
                titulo=f"Deck Candidate {index}",
                artista="Test",
                duracao_segundos=180,
                genero="Pop",
            )
        )

    playlist = playlist_uc.criar_deck_playlist_por_parametros(
        adult.usuario_id, "Filtered deck"
    )
    first_page, cursor, has_more = playlist_uc.obter_deck_playlist(
        playlist.playlist_id, adult.usuario_id, limite=10
    )
    assert len(first_page) == 10
    assert has_more is True
    assert cursor == first_page[-1].musica_id
    assert all(song.genero.lower() != "rock" for song in first_page)
    assert all(song.musica_id != rejected_song.musica_id for song in first_page)

    second_page, _, _ = playlist_uc.obter_deck_playlist(
        playlist.playlist_id, adult.usuario_id, limite=10, cursor_id=cursor
    )
    assert len(second_page) == 10
    assert {song.musica_id for song in first_page}.isdisjoint(
        song.musica_id for song in second_page
    )

    jam = jam_uc.criar_jam(adult.usuario_id, "Filtered jam", duracao_minutos=120)
    jam_page, _, jam_has_more = jam_uc.obter_deck_adicionar(
        jam.jam_id, adult.usuario_id, limite=10
    )
    assert len(jam_page) == 10
    assert jam_has_more is True
    assert all(song.genero.lower() != "rock" for song in jam_page)
    assert all(song.musica_id != rejected_song.musica_id for song in jam_page)

    family = plano_repo.buscar_por_nome("Família")
    titular = auth_uc.cadastrar_usuario(
        "filtered-minor-family@ribbit.com",
        "secretpassword",
        "Minor Family",
        40,
        family.plano_id,
    )
    child = perfil_uc.adicionar_membro_familia(
        titular.usuario_id,
        "filtered-minor@ribbit.com",
        "secretpassword",
        "Minor",
        date.today().replace(year=date.today().year - 14),
    )
    explicit_song = next(
        song for song in musica_repo.listar_ativas() if song.titulo == "Rap God"
    )
    minor_playlist = playlist_uc.criar_deck_playlist_por_parametros(
        child.usuario_id, "Minor playlist"
    )
    minor_playlist_page, _, _ = playlist_uc.obter_deck_playlist(
        minor_playlist.playlist_id, child.usuario_id, limite=100
    )
    assert all(not song.bloqueado_para_menores for song in minor_playlist_page)
    assert explicit_song.musica_id not in {
        song.musica_id for song in minor_playlist_page
    }

    minor_jam = jam_uc.criar_jam(titular.usuario_id, "Minor jam")
    jam_uc.entrar_na_jam(minor_jam.codigo_sala, child.usuario_id)
    minor_page, _, _ = jam_uc.obter_deck_adicionar(
        minor_jam.jam_id, child.usuario_id, limite=100
    )
    assert all(not song.bloqueado_para_menores for song in minor_page)
    assert explicit_song.musica_id not in {song.musica_id for song in minor_page}
