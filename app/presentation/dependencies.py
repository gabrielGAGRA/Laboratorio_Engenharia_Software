"""Dependency injection providers for repositories and application use cases."""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.application.admin_use_cases import AdminUseCases
from app.application.auth_use_cases import AuthUseCases
from app.application.descoberta_use_cases import DescobertaUseCases
from app.application.jam_use_cases import JamUseCases
from app.application.perfil_use_cases import PerfilUseCases
from app.application.playlist_use_cases import PlaylistUseCases
from app.application.review_use_cases import ReviewUseCases
from app.infrastructure.apis_externas import ExternalMusicServiceAdapter
from app.infrastructure.database import get_db
from app.infrastructure.repositories import (
    AvaliacaoRepository,
    InteracaoRepository,
    JamRepository,
    MusicaRepository,
    PlanoRepository,
    PlaylistRepository,
    UsuarioRepository,
)


def get_auth_use_cases(db: Session = Depends(get_db)) -> AuthUseCases:
    return AuthUseCases(
        usuario_repo=UsuarioRepository(db),
        plano_repo=PlanoRepository(db),
    )


def get_descoberta_use_cases(db: Session = Depends(get_db)) -> DescobertaUseCases:
    return DescobertaUseCases(
        usuario_repo=UsuarioRepository(db),
        musica_repo=MusicaRepository(db),
        interacao_repo=InteracaoRepository(db),
    )


def get_playlist_use_cases(db: Session = Depends(get_db)) -> PlaylistUseCases:
    return PlaylistUseCases(
        usuario_repo=UsuarioRepository(db),
        musica_repo=MusicaRepository(db),
        playlist_repo=PlaylistRepository(db),
        external_service=ExternalMusicServiceAdapter(),
    )


def get_perfil_use_cases(db: Session = Depends(get_db)) -> PerfilUseCases:
    return PerfilUseCases(
        usuario_repo=UsuarioRepository(db),
        plano_repo=PlanoRepository(db),
        interacao_repo=InteracaoRepository(db),
        musica_repo=MusicaRepository(db),
    )


def get_jam_use_cases(db: Session = Depends(get_db)) -> JamUseCases:
    return JamUseCases(
        jam_repo=JamRepository(db),
        usuario_repo=UsuarioRepository(db),
        musica_repo=MusicaRepository(db),
    )


def get_review_use_cases(db: Session = Depends(get_db)) -> ReviewUseCases:
    return ReviewUseCases(
        musica_repo=MusicaRepository(db),
        avaliacao_repo=AvaliacaoRepository(db),
        usuario_repo=UsuarioRepository(db),
    )


def get_admin_use_cases(db: Session = Depends(get_db)) -> AdminUseCases:
    return AdminUseCases(
        usuario_repo=UsuarioRepository(db),
        plano_repo=PlanoRepository(db),
        musica_repo=MusicaRepository(db),
        avaliacao_repo=AvaliacaoRepository(db),
    )
