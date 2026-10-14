"""Pydantic DTOs for API requests and responses."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class PlanoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    plano_id: int
    nome: str
    preco_mensal: float
    max_perfis: int


class UsuarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    usuario_id: int
    email: str
    nome_exibicao: str
    idade: int
    plano_id: int
    spotify_id: str | None = None
    titular_id: int | None = None
    generos_bloqueados: str | None = None
    is_admin: bool = False
    criado_em: datetime | None = None


class CadastroUsuarioRequest(BaseModel):
    email: EmailStr
    senha: str = Field(min_length=6)
    nome_exibicao: str = Field(min_length=2)
    idade: int = Field(ge=0)
    plano_id: int | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    senha: str


class AtualizarRestricaoMenoresRequest(BaseModel):
    bloqueado_para_menores: bool


class MusicaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    musica_id: int
    titulo: str
    artista: str
    duracao_segundos: int
    genero: str
    spotify_id: str | None = None
    album: str | None = None
    pais: str | None = None
    ano_lancamento: int | None = None
    capa_url: str | None = None
    itunes_preview_url: str | None = None
    bloqueado_para_menores: bool
    is_deleted: bool


class InteracaoRequest(BaseModel):
    usuario_id: int
    musica_id: int
    acao: str


class InteracaoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    interacao_id: int
    usuario_id: int
    musica_id: int
    acao: str
    criado_em: datetime | None = None


class DeckPlaylistRequest(BaseModel):
    usuario_id: int
    nome: str
    duracao_minutos: int | None = None
    genero: str | None = None
    ano: int | None = None
    artista: str | None = None
    pais: str | None = None
    descricao: str | None = None


class PlaylistResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    playlist_id: int
    usuario_id: int
    nome: str
    descricao: str | None = None
    spotify_playlist_id: str | None = None
    is_exportada: bool
    musicas: list[MusicaResponse] = []


class SwipeAddMusicaRequest(BaseModel):
    musica_id: int


class AtualizarPerfilRequest(BaseModel):
    nome_exibicao: str | None = None
    nova_senha: str | None = None


class VincularSpotifyRequest(BaseModel):
    usuario_id: int
    spotify_id: str


class AlterarPlanoRequest(BaseModel):
    usuario_id: int
    novo_plano_id: int


class TrocarInteracaoRequest(BaseModel):
    usuario_id: int
    musica_id: int
    nova_acao: str


class GenerosBloqueadosRequest(BaseModel):
    usuario_id: int
    generos_bloqueados: str


class AdicionarMembroFamiliaRequest(BaseModel):
    titular_id: int
    dependente_id: int


class CriarJamRequest(BaseModel):
    host_usuario_id: int
    nome_sala: str


class EntrarJamRequest(BaseModel):
    codigo_sala: str


class VotarMusicaJamRequest(BaseModel):
    usuario_id: int
    musica_id: int
    pontos: int = 1


class PularMusicaJamRequest(BaseModel):
    usuario_id: int
    musica_id: int


class JamFilaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    jam_fila_id: int
    jam_id: int
    musica_id: int
    pontos_voto: int


class JamResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    jam_id: int
    host_usuario_id: int
    nome_sala: str
    codigo_sala: str
    is_ativa: bool
    musica_atual_id: int | None = None


class JamEstadoResponse(BaseModel):
    jam: JamResponse
    musica_atual: MusicaResponse | None = None
    fila: list[JamFilaResponse] = []


class PublicarReviewRequest(BaseModel):
    usuario_id: int
    musica_id: int
    nota: int = Field(ge=1, le=5)
    texto: str | None = None


class ReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    avaliacao_id: int
    usuario_id: int
    musica_id: int
    nota: int
    texto: str | None = None
    likes_count: int
    is_deleted: bool
    criado_em: datetime | None = None


class AtualizarPlanoAdminRequest(BaseModel):
    novo_preco: float | None = None
    novo_nome: str | None = None
    max_perfis: int | None = None
