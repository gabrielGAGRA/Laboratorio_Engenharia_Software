"""Profile, plans, premium features, and family routes."""

from typing import Any

from fastapi import APIRouter, Depends, Query

from app.application.perfil_use_cases import PerfilUseCases
from app.domain.entities import Usuario
from app.presentation.dependencies import get_current_user, get_perfil_use_cases
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
    usuario: Usuario = Depends(get_current_user),
    use_cases: PerfilUseCases = Depends(get_perfil_use_cases),
) -> dict[str, Any]:
    dados = use_cases.obter_perfil_usuario(usuario.usuario_id)
    return {
        "usuario": UsuarioResponse.model_validate(dados["usuario"]),
        "plano": PlanoResponse.model_validate(dados["plano"]),
        "ultimas_interacoes": [
            InteracaoResponse.model_validate(item)
            for item in dados["interacoes_recentes"]
        ],
    }


@router.put("/api/perfil/me", response_model=UsuarioResponse)
def atualizar_perfil(
    req: AtualizarPerfilRequest,
    usuario: Usuario = Depends(get_current_user),
    use_cases: PerfilUseCases = Depends(get_perfil_use_cases),
) -> UsuarioResponse:
    atualizado = use_cases.atualizar_perfil(
        usuario_id=usuario.usuario_id,
        nome_exibicao=req.nome_exibicao,
        nova_senha=req.nova_senha,
    )
    return UsuarioResponse.model_validate(atualizado)


@router.post("/api/perfil/vincular-spotify", response_model=UsuarioResponse)
def vincular_spotify(
    req: VincularSpotifyRequest,
    usuario: Usuario = Depends(get_current_user),
    use_cases: PerfilUseCases = Depends(get_perfil_use_cases),
) -> UsuarioResponse:
    atualizado = use_cases.vincular_spotify(
        usuario_id=usuario.usuario_id,
        spotify_id=req.spotify_id,
    )
    return UsuarioResponse.model_validate(atualizado)


@router.get("/api/planos", response_model=list[PlanoResponse])
def listar_planos(
    use_cases: PerfilUseCases = Depends(get_perfil_use_cases),
) -> list[PlanoResponse]:
    return [
        PlanoResponse.model_validate(plano)
        for plano in use_cases.listar_planos_existentes()
    ]


@router.post("/api/perfil/plano", response_model=UsuarioResponse)
def alterar_plano(
    req: AlterarPlanoRequest,
    usuario: Usuario = Depends(get_current_user),
    use_cases: PerfilUseCases = Depends(get_perfil_use_cases),
) -> UsuarioResponse:
    atualizado = use_cases.alterar_plano_assinatura(
        usuario_id=usuario.usuario_id,
        novo_plano_id=req.novo_plano_id,
    )
    return UsuarioResponse.model_validate(atualizado)


@router.delete("/api/perfil/plano", response_model=UsuarioResponse)
def cancelar_plano(
    usuario: Usuario = Depends(get_current_user),
    use_cases: PerfilUseCases = Depends(get_perfil_use_cases),
) -> UsuarioResponse:
    atualizado = use_cases.cancelar_plano_assinatura(usuario_id=usuario.usuario_id)
    return UsuarioResponse.model_validate(atualizado)


@router.delete("/api/perfil/conta")
def excluir_conta(
    usuario: Usuario = Depends(get_current_user),
    use_cases: PerfilUseCases = Depends(get_perfil_use_cases),
) -> dict[str, bool]:
    return {"sucesso": use_cases.excluir_conta(usuario_id=usuario.usuario_id)}


@router.get("/api/perfil/dash")
@router.get("/api/perfil/frequencia", include_in_schema=False)
def dashboard_premium(
    usuario: Usuario = Depends(get_current_user),
    use_cases: PerfilUseCases = Depends(get_perfil_use_cases),
) -> dict[str, Any]:
    return use_cases.obter_dashboard_premium(usuario.usuario_id)


@router.put("/api/perfil/interacao", response_model=InteracaoResponse)
def trocar_interacao(
    req: TrocarInteracaoRequest,
    usuario: Usuario = Depends(get_current_user),
    use_cases: PerfilUseCases = Depends(get_perfil_use_cases),
) -> InteracaoResponse:
    interacao = use_cases.trocar_interacao_musica(
        usuario_id=usuario.usuario_id,
        musica_id=req.musica_id,
        nova_acao=req.nova_acao,
    )
    return InteracaoResponse.model_validate(interacao)


@router.get("/api/perfil/interacoes", response_model=list[InteracaoResponse])
@router.get("/api/perfil/historico", response_model=list[InteracaoResponse])
def obter_historico(
    categoria: str | None = Query(None),
    usuario: Usuario = Depends(get_current_user),
    use_cases: PerfilUseCases = Depends(get_perfil_use_cases),
) -> list[InteracaoResponse]:
    if categoria:
        itens = use_cases.obter_historico_por_categoria(usuario.usuario_id, categoria)
    else:
        use_cases.obter_frequencia_anual(usuario.usuario_id)
        itens = use_cases.listar_interacoes(usuario.usuario_id)
    return [InteracaoResponse.model_validate(item) for item in itens]


@router.get("/api/perfil/generos-bloqueados")
def listar_generos_bloqueados(
    usuario: Usuario = Depends(get_current_user),
    use_cases: PerfilUseCases = Depends(get_perfil_use_cases),
) -> list[str]:
    return use_cases.listar_generos_bloqueados(usuario.usuario_id)


@router.put("/api/perfil/generos-bloqueados", response_model=UsuarioResponse)
def editar_generos_bloqueados(
    req: GenerosBloqueadosRequest,
    usuario: Usuario = Depends(get_current_user),
    use_cases: PerfilUseCases = Depends(get_perfil_use_cases),
) -> UsuarioResponse:
    atualizado = use_cases.editar_generos_bloqueados(
        usuario_id=usuario.usuario_id,
        novos_generos=req.generos_bloqueados,
    )
    return UsuarioResponse.model_validate(atualizado)


@router.get("/api/perfil/familia/membros", response_model=list[UsuarioResponse])
def listar_membros_familia(
    usuario: Usuario = Depends(get_current_user),
    use_cases: PerfilUseCases = Depends(get_perfil_use_cases),
) -> list[UsuarioResponse]:
    membros = use_cases.listar_membros_familia(titular_id=usuario.usuario_id)
    return [UsuarioResponse.model_validate(membro) for membro in membros]


@router.post("/api/perfil/familia/membros", response_model=UsuarioResponse)
def adicionar_membro_familia(
    req: AdicionarMembroFamiliaRequest,
    titular: Usuario = Depends(get_current_user),
    use_cases: PerfilUseCases = Depends(get_perfil_use_cases),
) -> UsuarioResponse:
    membro = use_cases.adicionar_membro_familia(
        titular_id=titular.usuario_id,
        email=str(req.email),
        senha=req.senha,
        nome_exibicao=req.nome_exibicao,
        data_nascimento=req.data_nascimento,
    )
    return UsuarioResponse.model_validate(membro)


@router.delete(
    "/api/perfil/familia/membros/{membro_id}", response_model=UsuarioResponse
)
def remover_membro_familia(
    membro_id: int,
    titular: Usuario = Depends(get_current_user),
    use_cases: PerfilUseCases = Depends(get_perfil_use_cases),
) -> UsuarioResponse:
    desvinculado = use_cases.remover_membro_familia(
        titular_id=titular.usuario_id,
        membro_id=membro_id,
    )
    return UsuarioResponse.model_validate(desvinculado)
