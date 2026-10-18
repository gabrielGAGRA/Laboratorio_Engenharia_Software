"""Authentication and registration router."""

from fastapi import APIRouter, Depends, status

from app.application.auth_use_cases import AuthUseCases
from app.infrastructure.security import criar_access_token
from app.presentation.dependencies import get_auth_use_cases
from app.presentation.schemas import (
    CadastroUsuarioRequest,
    LoginRequest,
    LoginResponse,
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
        plano_id=req.plano_id,
        data_nascimento=req.data_nascimento,
    )
    return UsuarioResponse.model_validate(usuario)


@router.post("/login", response_model=LoginResponse)
def login(
    req: LoginRequest,
    use_cases: AuthUseCases = Depends(get_auth_use_cases),
) -> LoginResponse:
    usuario = use_cases.autenticar_usuario(email=req.email, senha=req.senha)
    return LoginResponse(
        access_token=criar_access_token(usuario.usuario_id),
        usuario=UsuarioResponse.model_validate(usuario),
    )
