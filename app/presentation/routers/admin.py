"""Administration routes protected by the authenticated admin role."""

from typing import Any

from fastapi import APIRouter, Depends

from app.application.admin_use_cases import AdminUseCases
from app.application.exceptions import BusinessRuleViolationError
from app.domain.entities import Usuario
from app.presentation.dependencies import get_admin_use_cases, get_current_admin
from app.presentation.schemas import (
    AtualizarAdminRequest,
    AtualizarPlanoAdminRequest,
    BloquearMusicaRequest,
    MusicaResponse,
    PlanoResponse,
    UsuarioResponse,
)

router = APIRouter(
    prefix="/api/admin",
    tags=["Admin Console"],
    dependencies=[Depends(get_current_admin)],
)


@router.get("/dashboard")
def dashboard_executivo(
    use_cases: AdminUseCases = Depends(get_admin_use_cases),
) -> dict[str, Any]:
    return use_cases.obter_dashboard_executivo()


@router.get("/audiencia")
def relatorio_audiencia(
    use_cases: AdminUseCases = Depends(get_admin_use_cases),
) -> dict[str, Any]:
    return use_cases.obter_relatorio_audiencia()


@router.get("/administradores", response_model=list[UsuarioResponse])
def listar_administradores(
    use_cases: AdminUseCases = Depends(get_admin_use_cases),
) -> list[UsuarioResponse]:
    return [
        UsuarioResponse.model_validate(usuario)
        for usuario in use_cases.listar_administradores()
    ]


@router.put("/administradores/{usuario_id}", response_model=UsuarioResponse)
def atualizar_administrador(
    usuario_id: int,
    req: AtualizarAdminRequest,
    administrador: Usuario = Depends(get_current_admin),
    use_cases: AdminUseCases = Depends(get_admin_use_cases),
) -> UsuarioResponse:
    if administrador.usuario_id == usuario_id and not req.is_admin:
        raise BusinessRuleViolationError(
            "O administrador autenticado não pode remover seu próprio acesso."
        )
    usuario = use_cases.atualizar_papel_admin(usuario_id, req.is_admin)
    return UsuarioResponse.model_validate(usuario)


@router.get("/musicas-bloqueadas", response_model=list[MusicaResponse])
def listar_musicas_bloqueadas(
    use_cases: AdminUseCases = Depends(get_admin_use_cases),
) -> list[MusicaResponse]:
    return [
        MusicaResponse.model_validate(musica)
        for musica in use_cases.listar_musicas_bloqueadas()
    ]


@router.put("/musicas/{musica_id}/bloquear")
def bloquear_musica(
    musica_id: int,
    req: BloquearMusicaRequest,
    use_cases: AdminUseCases = Depends(get_admin_use_cases),
) -> dict[str, int | bool]:
    return {
        "musica_id": musica_id,
        "bloqueada": use_cases.bloquear_musica(musica_id, req.bloqueada),
    }


@router.get("/planos", response_model=list[PlanoResponse])
def listar_planos(
    use_cases: AdminUseCases = Depends(get_admin_use_cases),
) -> list[PlanoResponse]:
    return [PlanoResponse.model_validate(plano) for plano in use_cases.listar_planos()]


@router.put("/planos/{plano_id}", response_model=PlanoResponse)
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
