# AI Guide: Domain Invariants, API Contract, and External Integration

---

## 1. Request Context & Routing

Rotas registradas sob o prefixo `/api`:

- `POST /api/auth/cadastrar` — cria conta; corpo: `CadastrarUsuarioRequest` (email, senha, nome, idade, plano_id)
- `POST /api/auth/login` — autentica; retorna `UsuarioResponse` com `usuario_id`
- `GET /api/descoberta/proxima?usuario_id={id}` — próxima música para swipe
- `POST /api/descoberta/interagir` — registra curtida/amada/rejeitada
- `POST /api/playlists/deck` — cria playlist por parâmetros (duração, vibe, época, país, gênero, artistas)
- `POST /api/playlists/{id}/swipe-add?usuario_id={id}` — adiciona música via swipe a uma playlist
- `GET /api/playlists` — lista playlists do usuário
- `POST /api/playlists/{id}/exportar-spotify` — exporta para Spotify
- `POST /api/jams` — cria sala Jam
- `POST /api/jams/entrar` — entra em sala por código
- `GET /api/jams/{id}/estado?usuario_id={id}` — estado atual da jam (faixas restritas são ocultadas para menores)
- `POST /api/jams/{id}/votar` — vota em uma música da fila; corpo inclui `usuario_id`
- `POST /api/jams/{id}/pular` — vota para pular música; corpo inclui `usuario_id`
- `GET /api/musicas/buscar?usuario_id={id}` — busca por artista, álbum, gênero, ano e respeita restrições etárias
- `POST /api/reviews` — publica review (nota 1–5 + texto)
- `GET /api/reviews/feed-top5dias` — top 3 reviews com mais likes nos últimos 5 dias
- `POST /api/reviews/{id}/like` — dá like em um comentário
- `GET /api/reviews/reviews-musica` — reviews de uma música específica
- `GET /api/perfil/me`, `PUT /api/perfil/me` — perfil do usuário logado
- `POST /api/perfil/vincular-spotify` — vincula conta Spotify
- `GET /api/planos`, `POST /api/perfil/plano`, `DELETE /api/perfil/plano` — gestão de assinatura
- `DELETE /api/perfil/conta` — exclusão de conta
- `GET /api/perfil/frequencia` _(Premium)_ — dashboard anual (42h, gêneros/artistas favoritos)
- `PUT /api/perfil/interacao` _(Premium)_ — muda tipo de interação (curtida ↔ amada ↔ rejeitada)
- `GET /api/perfil/historico` _(Premium)_ — histórico completo por categoria
- `GET/PUT /api/perfil/generos-bloqueados` _(Premium)_ — edita gêneros bloqueados
- `GET /api/perfil/familia/membros`, `POST`, `DELETE /{membro_id}` — gestão de família (Titular)
- `GET /api/admin/dashboard` — receita líquida por plano
- `GET /api/admin/usuarios` — listagem de usuários
- `GET /api/admin/audiencia` — relatório de audiência
- `POST /api/admin/musicas/{id}/bloquear` — soft delete (`is_deleted = True`)
- `PUT /api/admin/musicas/{id}/restricao-menores` — define `bloqueado_para_menores` com corpo `{"bloqueado_para_menores": true|false}`
- `PUT /api/admin/usuarios/{id}/promover-admin` — promove usuário a admin
- `PUT /api/admin/planos/{id}` — atualiza plano existente
- `GET /api/admin/comentarios` — top comentários

**Identity & Context nos payloads**:
- Os endpoints de usuário recebem `usuario_id` em query ou no corpo, conforme cada rota; esse ID é contexto informado pelo cliente, não uma sessão autenticada.
- `X-Admin-Id` (header) — identifica o admin; obrigatório nas rotas administrativas protegidas (exceto login).
- Campos de corpo: validados via DTOs Pydantic em `app/presentation/schemas.py`.

**Headers para APIs externas**:
- Spotify: `Authorization: Bearer <token>` obtido via Client Credentials; variáveis `SPOTIFY_CLIENT_ID` / `SPOTIFY_CLIENT_SECRET`
- iTunes: nenhum header de autenticação (API pública)

---

## 2. Domain Validation Invariants

### Trava de Menor de Idade
- `IDADE_MINIMA_ADULTO = 18` (constante em `descoberta_use_cases.py`)
- Músicas com `bloqueado_para_menores = True` são filtradas quando `usuario.idade < 18`
- Aplicada na descoberta, busca do catálogo, geração e adição manual a playlists, e inclusão/voto de músicas na fila de Jams

### Gêneros Bloqueados
- `usuario.generos_bloqueados: list[str]` — lista de gêneros que o usuário não quer ver
- Filtrado em `obter_proxima_musica_swipe` e `criar_deck_playlist_por_parametros`

### Validação de Plano
- Premium obrigatório: `obter_frequencia_anual`, `trocar_interacao_musica`, `obter_historico_por_categoria`, `editar_generos_bloqueados`
- Família: `adicionar_membro_familia` valida `plano.max_perfis > 1` e conta dependentes já vinculados
- Free: plano padrão retornado ao cancelar (`cancelar_plano_assinatura`)

### Integridade de Playlist (IDOR)
- `playlist_use_cases.py` valida `playlist.usuario_id == usuario_id` antes de qualquer escrita

### Reviews
- `NOTA_MINIMA = 1`, `NOTA_MAXIMA = 5` — constantes em `review_use_cases.py`
- `obter_reviews_por_musica` verifica `musica.is_deleted` antes de retornar

### Soft Delete de Músicas
- `musica.is_deleted = True` oculta a faixa de buscas, descobertas e playlists novas
- O registro permanece nos históricos de interação para integridade de auditoria

### Violation Handling

- Qualquer violação lança subclasse de `CustomError` (`app/domain/exceptions.py`)
- `app/main.py` tem exception handlers globais que mapeiam cada tipo para o status HTTP correspondente:
  - `EntityNotFoundError` → 404
  - `BusinessRuleViolationError` → 400
  - `DuplicateEntityError` → 409
  - `UnauthorizedError` → 401
  - `ForbiddenError` → 403

---

## 3. External I/O & Path Rules

**Spotify REST API** (`app/infrastructure/apis_externas.py`):
- Busca: `GET https://api.spotify.com/v1/search?q=...&type=track`
- Playback context: `GET https://api.spotify.com/v1/tracks/{id}`
- Exportação: `POST https://api.spotify.com/v1/users/{user_id}/playlists` + `POST .../tracks`
- Token via Client Credentials Flow (sem interação do usuário)

**iTunes Search API**:
- Busca fallback: `GET https://itunes.apple.com/search?term=...&entity=song`
- Preview mp3: campo `previewUrl` no resultado — salvo em `musica.itunes_preview_url`

---

## 4. Execution / Isolation

- Banco padrão: SQLite (`sqlite:///./ribbit_local.db`) — sem configuração necessária localmente
- Banco produção: PostgreSQL via `DATABASE_URL` env var
- Testes usam `sqlite:///:memory:` — banco recriado a cada execução de teste
- `seed.py` é idempotente: verifica existência antes de inserir

---

## 5. Execution Result & Message Formatting

- Use cases retornam entidades de domínio (`dataclasses`) ou primitivos Python
- Routers convertem para DTOs Pydantic de resposta antes de retornar ao cliente
- Erros retornam `{"erro": "<tipo>", "mensagem": "<mensagem>", "detalhes": {}}` com o status HTTP correspondente
- Nenhum use case retorna objetos FastAPI `Response` ou `JSONResponse` diretamente
