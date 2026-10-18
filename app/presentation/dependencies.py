"""Dependency injection providers for repositories and application use cases."""

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.application.admin_use_cases import AdminUseCases
from app.application.auth_use_cases import AuthUseCases
from app.application.descoberta_use_cases import DescobertaUseCases
from app.application.exceptions import (
    EntityNotFoundError,
    ForbiddenError,
    UnauthorizedError,
)
from app.application.jam_use_cases import JamUseCases
from app.application.perfil_use_cases import PerfilUseCases
from app.application.playlist_use_cases import PlaylistUseCases
from app.application.review_use_cases import ReviewUseCases
from app.domain.entities import Usuario
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
from app.infrastructure.security import decodificar_access_token

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    """Resolve the authenticated user from a signed bearer token."""
    if not credentials:
        raise UnauthorizedError("Credencial de autenticação ausente.")
    try:
        usuario_id = decodificar_access_token(credentials.credentials)
    except ValueError as exc:
        raise UnauthorizedError("Token de acesso inválido.") from exc
    usuario = UsuarioRepository(db).buscar_por_id(usuario_id)
    if not usuario:
        raise EntityNotFoundError("Usuário do token não encontrado.")
    return usuario


def get_current_admin(usuario: Usuario = Depends(get_current_user)) -> Usuario:
    """Reject requests from authenticated users without admin privileges."""
    if not usuario.is_admin:
        raise ForbiddenError("Acesso restrito a administradores.")
    return usuario


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
        external_service=ExternalMusicServiceAdapter(),
    )


def get_playlist_use_cases(db: Session = Depends(get_db)) -> PlaylistUseCases:
    return PlaylistUseCases(
        usuario_repo=UsuarioRepository(db),
        musica_repo=MusicaRepository(db),
        playlist_repo=PlaylistRepository(db),
        external_service=ExternalMusicServiceAdapter(),
        interacao_repo=InteracaoRepository(db),
    )


def get_perfil_use_cases(db: Session = Depends(get_db)) -> PerfilUseCases:
    return PerfilUseCases(
        usuario_repo=UsuarioRepository(db),
        plano_repo=PlanoRepository(db),
        interacao_repo=InteracaoRepository(db),
        musica_repo=MusicaRepository(db),
        playlist_repo=PlaylistRepository(db),
    )


def get_jam_use_cases(db: Session = Depends(get_db)) -> JamUseCases:
    return JamUseCases(
        jam_repo=JamRepository(db),
        usuario_repo=UsuarioRepository(db),
        musica_repo=MusicaRepository(db),
        interacao_repo=InteracaoRepository(db),
        playlist_repo=PlaylistRepository(db),
    )


def get_review_use_cases(db: Session = Depends(get_db)) -> ReviewUseCases:
    return ReviewUseCases(
        musica_repo=MusicaRepository(db),
        avaliacao_repo=AvaliacaoRepository(db),
        usuario_repo=UsuarioRepository(db),
        interacao_repo=InteracaoRepository(db),
        playlist_repo=PlaylistRepository(db),
        external_service=ExternalMusicServiceAdapter(),
    )


def get_admin_use_cases(db: Session = Depends(get_db)) -> AdminUseCases:
    return AdminUseCases(
        usuario_repo=UsuarioRepository(db),
        plano_repo=PlanoRepository(db),
        musica_repo=MusicaRepository(db),
        avaliacao_repo=AvaliacaoRepository(db),
    )
