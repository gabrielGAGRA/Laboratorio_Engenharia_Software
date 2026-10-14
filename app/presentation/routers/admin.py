"""Administration console router for catalog moderation and executive dashboard."""

from typing import Any

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from app.application.admin_use_cases import AdminUseCases
from app.application.auth_use_cases import AuthUseCases
from app.domain.entities import Usuario
from app.domain.exceptions import ForbiddenError, UnauthorizedError
from app.infrastructure.database import get_db
from app.infrastructure.repositories import UsuarioRepository
from app.presentation.dependencies import get_admin_use_cases, get_auth_use_cases
from app.presentation.schemas import (
    AtualizarRestricaoMenoresRequest,
    AtualizarPlanoAdminRequest,
    LoginRequest,
    PlanoResponse,
    UsuarioResponse,
)

router = APIRouter(prefix="/api/admin", tags=["Admin Console"])


def verificar_admin(
    admin_id: int | None = Header(None, alias="X-Admin-Id"),
    db: Session = Depends(get_db),
) -> Usuario:
    """Valida se a requisição possui credencial de administrador válida."""
    if admin_id is None:
        raise UnauthorizedError("Identificação de administrador ausente.")
    usuario = UsuarioRepository(db).buscar_por_id(admin_id)
    if not usuario or not usuario.is_admin:
        raise ForbiddenError("Acesso restrito a administradores.")
    return usuario


@router.post("/login", response_model=UsuarioResponse)
def login_admin(
    req: LoginRequest,
    auth_use_cases: AuthUseCases = Depends(get_auth_use_cases),
) -> UsuarioResponse:
    admin = auth_use_cases.login_admin(email=req.email, senha=req.senha)
    return UsuarioResponse.model_validate(admin)


@router.get("/dashboard", dependencies=[Depends(verificar_admin)])
def dashboard_executivo(
    use_cases: AdminUseCases = Depends(get_admin_use_cases),
) -> dict[str, Any]:
    return use_cases.obter_dashboard_executivo()


@router.get("/usuarios", dependencies=[Depends(verificar_admin)])
def gerenciar_usuarios(
    use_cases: AdminUseCases = Depends(get_admin_use_cases),
) -> list[dict[str, Any]]:
    return use_cases.gerenciar_usuarios_planos()


@router.get("/audiencia", dependencies=[Depends(verificar_admin)])
def relatorio_audiencia(
    use_cases: AdminUseCases = Depends(get_admin_use_cases),
) -> dict[str, Any]:
    return use_cases.obter_relatorio_audiencia()


@router.post("/musicas/{musica_id}/bloquear", dependencies=[Depends(verificar_admin)])
def bloquear_musica(
    musica_id: int,
    use_cases: AdminUseCases = Depends(get_admin_use_cases),
) -> dict[str, bool]:
    sucesso = use_cases.bloquear_musica(musica_id=musica_id)
    return {"bloqueado": sucesso}


@router.put(
    "/musicas/{musica_id}/restricao-menores",
    dependencies=[Depends(verificar_admin)],
)
def atualizar_restricao_menores(
    musica_id: int,
    req: AtualizarRestricaoMenoresRequest,
    use_cases: AdminUseCases = Depends(get_admin_use_cases),
) -> dict[str, int | bool]:
    bloqueado = use_cases.atualizar_restricao_menores(
        musica_id=musica_id,
        bloqueado_para_menores=req.bloqueado_para_menores,
    )
    return {"musica_id": musica_id, "bloqueado_para_menores": bloqueado}


@router.put(
    "/usuarios/{usuario_id}/promover-admin",
    response_model=UsuarioResponse,
    dependencies=[Depends(verificar_admin)],
)
def promover_admin(
    usuario_id: int,
    use_cases: AdminUseCases = Depends(get_admin_use_cases),
) -> UsuarioResponse:
    usuario = use_cases.promover_usuario_para_admin(usuario_id=usuario_id)
    return UsuarioResponse.model_validate(usuario)


@router.put(
    "/planos/{plano_id}",
    response_model=PlanoResponse,
    dependencies=[Depends(verificar_admin)],
)
def atualizar_plano(
    plano_id: int,
    req: AtualizarPlanoAdminRequest,
    use_cases: AdminUseCases = Depends(get_admin_use_cases),
) -> PlanoResponse:
    plano = use_cases.atualizar_planos_existentes(
        plano_id=plano_id,
        novo_preco=req.novo_preco,
        novo_nome=req.novo_nome,
        max_perfis=req.max_perfis,
    )
    return PlanoResponse.model_validate(plano)


@router.get("/comentarios", dependencies=[Depends(verificar_admin)])
def top_comentarios(
    use_cases: AdminUseCases = Depends(get_admin_use_cases),
) -> list[dict[str, Any]]:
    return use_cases.ver_top_comentarios()
