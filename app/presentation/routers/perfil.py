"""User profile, subscription plans, premium, and family plan router."""

from typing import Any

from fastapi import APIRouter, Depends, Query

from app.application.perfil_use_cases import PerfilUseCases
from app.presentation.dependencies import get_perfil_use_cases
from app.presentation.schemas import (
    AdicionarMembroFamiliaRequest,
    AlterarPlanoRequest,
    AtualizarPerfilRequest,
    GenerosBloqueadosRequest,
    InteracaoResponse,
    PlanoResponse,
    TrocarInteracaoRequest,
    UsuarioResponse,
    VincularSpotifyRequest,
)

router = APIRouter(tags=["Perfil & Planos"])


@router.get("/api/perfil/me")
def obter_perfil(
    usuario_id: int = Query(...),
    use_cases: PerfilUseCases = Depends(get_perfil_use_cases),
) -> dict[str, Any]:
    dados = use_cases.obter_perfil_usuario(usuario_id=usuario_id)
    return {
        "usuario": UsuarioResponse.model_validate(dados["usuario"]),
        "plano": PlanoResponse.model_validate(dados["plano"]),
    }


@router.put("/api/perfil/me", response_model=UsuarioResponse)
def atualizar_perfil(
    usuario_id: int = Query(...),
    req: AtualizarPerfilRequest = ...,
    use_cases: PerfilUseCases = Depends(get_perfil_use_cases),
) -> UsuarioResponse:
    usuario = use_cases.atualizar_perfil(
        usuario_id=usuario_id,
        nome_exibicao=req.nome_exibicao,
        nova_senha=req.nova_senha,
    )
    return UsuarioResponse.model_validate(usuario)


@router.post("/api/perfil/vincular-spotify", response_model=UsuarioResponse)
def vincular_spotify(
    req: VincularSpotifyRequest,
    use_cases: PerfilUseCases = Depends(get_perfil_use_cases),
) -> UsuarioResponse:
    usuario = use_cases.vincular_spotify(
        usuario_id=req.usuario_id,
        spotify_id=req.spotify_id,
    )
    return UsuarioResponse.model_validate(usuario)


@router.get("/api/planos", response_model=list[PlanoResponse])
def listar_planos(
    use_cases: PerfilUseCases = Depends(get_perfil_use_cases),
) -> list[PlanoResponse]:
    planos = use_cases.listar_planos_existentes()
    return [PlanoResponse.model_validate(p) for p in planos]


@router.post("/api/perfil/plano", response_model=UsuarioResponse)
def alterar_plano(
    req: AlterarPlanoRequest,
    use_cases: PerfilUseCases = Depends(get_perfil_use_cases),
) -> UsuarioResponse:
    usuario = use_cases.alterar_plano_assinatura(
        usuario_id=req.usuario_id,
        novo_plano_id=req.novo_plano_id,
    )
    return UsuarioResponse.model_validate(usuario)


@router.delete("/api/perfil/plano", response_model=UsuarioResponse)
def cancelar_plano(
    usuario_id: int = Query(...),
    use_cases: PerfilUseCases = Depends(get_perfil_use_cases),
) -> UsuarioResponse:
    usuario = use_cases.cancelar_plano_assinatura(usuario_id=usuario_id)
    return UsuarioResponse.model_validate(usuario)


@router.delete("/api/perfil/conta")
def excluir_conta(
    usuario_id: int = Query(...),
    use_cases: PerfilUseCases = Depends(get_perfil_use_cases),
) -> dict[str, bool]:
    sucesso = use_cases.excluir_conta(usuario_id=usuario_id)
    return {"sucesso": sucesso}


# --- Rotas Premium ---


@router.get("/api/perfil/frequencia")
def obter_frequencia(
    usuario_id: int = Query(...),
    use_cases: PerfilUseCases = Depends(get_perfil_use_cases),
) -> dict[str, Any]:
    return use_cases.obter_frequencia_anual(usuario_id=usuario_id)


@router.put("/api/perfil/interacao", response_model=InteracaoResponse)
def trocar_interacao(
    req: TrocarInteracaoRequest,
    use_cases: PerfilUseCases = Depends(get_perfil_use_cases),
) -> InteracaoResponse:
    interacao = use_cases.trocar_interacao_musica(
        usuario_id=req.usuario_id,
        musica_id=req.musica_id,
        nova_acao=req.nova_acao,
    )
    return InteracaoResponse.model_validate(interacao)


@router.get("/api/perfil/historico", response_model=list[InteracaoResponse])
def obter_historico(
    usuario_id: int = Query(...),
    categoria: str | None = Query(None),
    use_cases: PerfilUseCases = Depends(get_perfil_use_cases),
) -> list[InteracaoResponse]:
    itens = use_cases.listar_interacoes(usuario_id=usuario_id, acao=categoria)
    return [InteracaoResponse.model_validate(i) for i in itens]


@router.get("/api/perfil/generos-bloqueados")
def listar_generos_bloqueados(
    usuario_id: int = Query(...),
    use_cases: PerfilUseCases = Depends(get_perfil_use_cases),
) -> list[str]:
    return use_cases.listar_generos_bloqueados(usuario_id=usuario_id)


@router.put("/api/perfil/generos-bloqueados", response_model=UsuarioResponse)
def editar_generos_bloqueados(
    req: GenerosBloqueadosRequest,
    use_cases: PerfilUseCases = Depends(get_perfil_use_cases),
) -> UsuarioResponse:
    usuario = use_cases.editar_generos_bloqueados(
        usuario_id=req.usuario_id,
        novos_generos=req.generos_bloqueados,
    )
    return UsuarioResponse.model_validate(usuario)


# --- Rotas Plano Família ---


@router.get("/api/perfil/familia/membros", response_model=list[UsuarioResponse])
def listar_membros_familia(
    titular_id: int = Query(...),
    use_cases: PerfilUseCases = Depends(get_perfil_use_cases),
) -> list[UsuarioResponse]:
    membros = use_cases.listar_membros_familia(titular_id=titular_id)
    return [UsuarioResponse.model_validate(m) for m in membros]


@router.post("/api/perfil/familia/membros", response_model=UsuarioResponse)
def adicionar_membro_familia(
    req: AdicionarMembroFamiliaRequest,
    use_cases: PerfilUseCases = Depends(get_perfil_use_cases),
) -> UsuarioResponse:
    dependente = use_cases.adicionar_membro_familia(
        titular_id=req.titular_id,
        dependente_id=req.dependente_id,
    )
    return UsuarioResponse.model_validate(dependente)


@router.delete(
    "/api/perfil/familia/membros/{membro_id}", response_model=UsuarioResponse
)
def remover_membro_familia(
    membro_id: int,
    titular_id: int = Query(...),
    use_cases: PerfilUseCases = Depends(get_perfil_use_cases),
) -> UsuarioResponse:
    desvinculado = use_cases.remover_membro_familia(
        titular_id=titular_id,
        membro_id=membro_id,
    )
    return UsuarioResponse.model_validate(desvinculado)
