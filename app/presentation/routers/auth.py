"""Authentication and registration router."""

from fastapi import APIRouter, Depends, status

from app.application.auth_use_cases import AuthUseCases
from app.presentation.dependencies import get_auth_use_cases
from app.presentation.schemas import (
    CadastroUsuarioRequest,
    LoginRequest,
    UsuarioResponse,
)

router = APIRouter(prefix="/api/auth", tags=["Autenticação"])


@router.post(
    "/cadastrar",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
)
def cadastrar(
    req: CadastroUsuarioRequest,
    use_cases: AuthUseCases = Depends(get_auth_use_cases),
) -> UsuarioResponse:
    usuario = use_cases.cadastrar_usuario(
        email=req.email,
        senha=req.senha,
        nome_exibicao=req.nome_exibicao,
        idade=req.idade,
        plano_id=req.plano_id,
    )
    return UsuarioResponse.model_validate(usuario)


@router.post("/login", response_model=UsuarioResponse)
def login(
    req: LoginRequest,
    use_cases: AuthUseCases = Depends(get_auth_use_cases),
) -> UsuarioResponse:
    usuario = use_cases.autenticar_usuario(email=req.email, senha=req.senha)
    return UsuarioResponse.model_validate(usuario)
