"""Ribbit Platform Backend V0 - FastAPI Application Root."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.domain.exceptions import (
    BusinessRuleViolationError,
    CustomError,
    DuplicateEntityError,
    EntityNotFoundError,
    ForbiddenError,
    UnauthorizedError,
)
from app.infrastructure.database import Base, SessionLocal, engine
from app.infrastructure.seed import run_seed
from app.presentation.routers.admin import router as admin_router
from app.presentation.routers.auth import router as auth_router
from app.presentation.routers.descoberta import router as descoberta_router
from app.presentation.routers.jams import router as jams_router
from app.presentation.routers.musicas_reviews import router as musicas_reviews_router
from app.presentation.routers.perfil import router as perfil_router
from app.presentation.routers.playlists import router as playlists_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Inicialização das tabelas e execução do seed de dados locais."""
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        run_seed(session)
    finally:
        session.close()
    yield


app = FastAPI(
    title="Ribbit Platform API",
    description="Backend V0 com Arquitetura Hexagonal para Descoberta Musical e Jams Colaborativas",
    version="0.1.0",
    lifespan=lifespan,
)

# Inclusão dos Routers
app.include_router(auth_router)
app.include_router(descoberta_router)
app.include_router(playlists_router)
app.include_router(perfil_router)
app.include_router(jams_router)
app.include_router(musicas_reviews_router)
app.include_router(admin_router)


# Mapeamento Global de Exceções de Domínio para HTTP
@app.exception_handler(EntityNotFoundError)
async def entity_not_found_handler(
    request: Request, exc: EntityNotFoundError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"erro": exc.name, "mensagem": exc.message, "detalhes": exc.details},
    )


@app.exception_handler(UnauthorizedError)
async def unauthorized_handler(
    request: Request, exc: UnauthorizedError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"erro": exc.name, "mensagem": exc.message, "detalhes": exc.details},
    )


@app.exception_handler(ForbiddenError)
async def forbidden_handler(request: Request, exc: ForbiddenError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"erro": exc.name, "mensagem": exc.message, "detalhes": exc.details},
    )


@app.exception_handler(DuplicateEntityError)
async def duplicate_entity_handler(
    request: Request, exc: DuplicateEntityError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"erro": exc.name, "mensagem": exc.message, "detalhes": exc.details},
    )


@app.exception_handler(BusinessRuleViolationError)
async def business_rule_handler(
    request: Request, exc: BusinessRuleViolationError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"erro": exc.name, "mensagem": exc.message, "detalhes": exc.details},
    )


@app.exception_handler(CustomError)
async def custom_domain_error_handler(
    request: Request, exc: CustomError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"erro": exc.name, "mensagem": exc.message, "detalhes": exc.details},
    )


@app.get("/")
def root() -> dict[str, str]:
    return {"status": "online", "app": "Ribbit API V0"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy"}
