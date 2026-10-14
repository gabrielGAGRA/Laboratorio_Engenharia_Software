# AI Guide: Hexagonal Architecture & Package Layout

---

## Layer Map & Package Responsibilities

**Composition root**: `app/main.py` — instancia a aplicação FastAPI, registra os sete routers via `include_router` e executa `popular_dados_iniciais()` (seed) no evento `lifespan`.

---

### Domain Layer (`app/domain/`)

- **`entities.py`**: Dataclasses puras sem dependência de frameworks.
  - `Plano`, `Usuario`, `Musica`, `Interacao`, `Playlist`, `PlaylistMusica`, `Jam`, `JamFila`, `AvaliacaoComentario`
  - `AcaoInteracao` — `StrEnum` com valores `curtida`, `amada`, `rejeitada`
- **`ports.py`**: Contratos abstratos (`ABC`) que o domínio exige mas não implementa:
  - Repositórios: `UsuarioRepositoryPort`, `PlanoRepositoryPort`, `MusicaRepositoryPort`, `InteracaoRepositoryPort`, `PlaylistRepositoryPort`, `JamRepositoryPort`, `AvaliacaoRepositoryPort`
  - Serviço externo: `ExternalMusicServicePort` (busca Spotify/iTunes, preview mp3, playback, exportação de playlist)
- **`exceptions.py`**: Hierarquia `CustomError → DomainError | EntityNotFoundError | BusinessRuleViolationError | DuplicateEntityError | UnauthorizedError | ForbiddenError`. Nunca importar HTTP ou FastAPI aqui.

---

### Application Layer (`app/application/`)

Cada arquivo contém funções de caso de uso que recebem dependências injetadas no construtor. Não importam SQLAlchemy, FastAPI ou Pydantic.

- `auth_use_cases.py` — cadastro (PBKDF2/HMAC-SHA256), autenticação, login admin
- `descoberta_use_cases.py` — próxima música com trava de menor de idade (`IDADE_MINIMA_ADULTO = 18`) e filtro de gêneros bloqueados
- `playlist_use_cases.py` — deck por parâmetros, add via swipe, listar biblioteca, exportar para Spotify; validação IDOR (playlist pertence ao usuário)
- `perfil_use_cases.py` — perfil, plano, família (titular/dependente), estatísticas Premium, histórico e gêneros bloqueados
- `jam_use_cases.py` — criar sala (`secrets.choice` para código), entrar, votar, pular, promover campeã de votos
- `review_use_cases.py` — busca de músicas, publicar review (`NOTA_MINIMA=1`, `NOTA_MAXIMA=5`), feed de comunidade (top 3 dos últimos 5 dias), likes
- `admin_use_cases.py` — dashboard financeiro (receita apenas de titulares), gestão de usuários/planos, auditoria, bloquear música (soft delete), promover admin

---

### Infrastructure Layer (`app/infrastructure/`)

Implementa os ports do domínio. Única camada que importa SQLAlchemy.

- **`database.py`**: Engine SQLAlchemy, `SessionLocal`, `get_db()` (gerador para DI). Suporta SQLite local (default) e PostgreSQL via `DATABASE_URL`.
- **`db_models.py`**: 9 modelos ORM mapeando as tabelas: `PlanoModel`, `UsuarioModel`, `MusicaModel`, `InteracaoModel`, `PlaylistModel`, `PlaylistMusicaModel`, `JamModel`, `JamFilaModel`, `AvaliacaoComentarioModel`.
- **`repositories.py`**: Implementações concretas dos 7 `RepositoryPort`. Responsáveis pelo mapeamento ORM ↔ Entidade de domínio.
- **`apis_externas.py`**: `SpotifyAdapter` (busca, playback context, exportação de playlist via API REST) e `ItunesAdapter` (fallback de busca e preview mp3). Usa `httpx` com catch de `httpx.HTTPError`.
- **`seed.py`**: `popular_dados_iniciais(db)` — verifica e insere 3 planos (Free R$0, Individual R$14,90, Família R$27,90) e 5 músicas de amostra. **Apenas para desenvolvimento local.**

---

### Presentation Layer (`app/presentation/`)

Endpoints enxutos: recebem HTTP → validam DTO → invocam use case → retornam resposta.

- **`schemas.py`**: DTOs Pydantic v2 para todas as requisições e respostas.
- **`dependencies.py`**: Provedores de DI que instanciam repositórios + use cases via `Depends`.
- **`routers/`**:
  - `auth.py` — `POST /api/auth/cadastrar`, `POST /api/auth/login`
  - `descoberta.py` — `GET /api/descoberta/proxima`, `POST /api/descoberta/interagir`
  - `playlists.py` — `POST /api/playlists/deck`, `POST /api/playlists/{id}/swipe-add`, `GET /api/playlists`, `POST /api/playlists/{id}/exportar-spotify`
  - `jams.py` — `POST /api/jams`, `POST /api/jams/entrar`, `GET /api/jams/{id}/estado`, `POST /api/jams/{id}/votar`, `POST /api/jams/{id}/pular`
  - `musicas_reviews.py` — `GET /api/musicas/buscar`, `POST /api/reviews`, `GET /api/reviews/feed-top5dias`, `POST /api/reviews/{id}/like`, `GET /api/reviews/reviews-musica`
  - `perfil.py` — perfil, planos, família, frequência anual (Premium), histórico (Premium), gêneros bloqueados (Premium)
  - `admin.py` — dashboard, usuários, audiência, bloquear música, promover admin, planos, comentários (todos protegidos por `X-Admin-Id`)

---

## Layer Crossing Rules

| ✅ Permitido | ❌ Proibido |
| --- | --- |
| `presentation` importa `application` | `domain` importar qualquer lib externa |
| `application` importa `domain` | `application` importar SQLAlchemy ou FastAPI |
| `infrastructure` importa `domain` (ports) | `infrastructure` importar use cases |
| `presentation` importa `infrastructure` (via DI em `dependencies.py`) | Qualquer camada importar a superior |
