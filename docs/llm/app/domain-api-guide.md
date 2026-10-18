# Backend API and Domain Rules

## Authentication and request identity

- `POST /api/auth/cadastrar` accepts name, e-mail, password, and date of birth. Direct registration rejects anyone under 18.
- `POST /api/auth/login` uses the same flow for regular and administrator accounts and returns a signed Bearer token.
- Protected user routes derive the account ID from `Authorization: Bearer <token>`; clients must not send a trusted user ID.
- Administrator routes additionally require the authenticated account to have `is_admin == true`.
- Set `RIBBIT_SECRET_KEY` to a persistent random secret in production. Production startup fails if it is missing.
- Local development seeds `admin@ribbit.example.com` with password `RibbitLocal2026!`. Override these with `RIBBIT_ADMIN_EMAIL` and `RIBBIT_ADMIN_PASSWORD`; the local seed is disabled when `RIBBIT_ENV=production`.

## Routes

### Authentication and plans

- `POST /api/auth/cadastrar`, `POST /api/auth/login`
- `GET /api/planos`, `POST /api/perfil/plano`, `DELETE /api/perfil/plano`

### Discovery and playlists

- `GET /api/descoberta/proxima`, `POST /api/descoberta/interagir`
- `GET /api/playlists`, `POST /api/playlists/deck`
- `GET /api/playlists/{id}/deck`, `POST /api/playlists/{id}/swipe-add`
- `GET /api/playlists/{id}`, `DELETE /api/playlists/{id}`
- `DELETE /api/playlists/{id}/musicas/{musica_id}`
- `POST /api/playlists/{id}/exportar-spotify` (mock adapter)

### Jams

- `POST /api/jams`, `POST /api/jams/entrar`
- `GET /api/jams/{id}/estado`, `POST /api/jams/{id}/votar-pular`
- `POST /api/jams/{id}/curtir-fila`, `GET /api/jams/{id}/deck-adicionar`
- `POST /api/jams/{id}/interagir-deck`, `POST /api/jams/{id}/encerrar`

Playlist and Jam suggestion endpoints return cursor-paginated objects:
`{"items": [...], "next_cursor": 123, "has_more": true}`. Requests accept `limite`
(default 20, maximum 100) and `cursor_id` (the previous page's `next_cursor`). The playlist
creation endpoint creates an empty playlist; fetch suggestions from its `/deck` route.

### Reviews and search

- `GET /api/reviews/ultimas-interagidas`, `GET /api/reviews/feed-top5dias`
- `POST /api/reviews/{id}/like`, `POST /api/reviews/{musica_id}/curtir-busca`
- `GET /api/reviews/musica/{musica_id}`, `POST /api/reviews`
- `DELETE /api/reviews/{review_id}`, `GET /api/musicas/buscar`

### Profile and family

- `GET /api/perfil/me`, `PUT /api/perfil/me`
- `POST /api/perfil/vincular-spotify`, `DELETE /api/perfil/conta`
- `GET /api/perfil/interacoes`, `PUT /api/perfil/interacao`
- `GET /api/perfil/dash`, `GET/PUT /api/perfil/generos-bloqueados`
- `GET/POST /api/perfil/familia/membros`
- `DELETE /api/perfil/familia/membros/{membro_id}`

Family membership management is restricted to the titular of a Family plan. Dependents under
18 can only be created through the family-member route.

### Administration

- `GET /api/admin/dashboard`, `GET /api/admin/audiencia`
- `GET /api/admin/administradores`, `PUT /api/admin/administradores/{id}`
- `GET /api/admin/musicas-bloqueadas`, `PUT /api/admin/musicas/{id}/bloquear`
- `GET /api/admin/planos`, `PUT /api/admin/planos/{id}`

## Business invariants

- Discovery, playlist decks, playlist additions, Jam suggestions, and Jam queue actions exclude
  deleted music, music blocked for minors, and genres blocked by the requesting user.
- Playlist and Jam decks omit tracks the requesting user previously rejected. Playlist decks
  return paginated candidates that fit the remaining duration; adding a track enforces the
  actual playlist duration limit. Jam free-source decks are paginated from the catalog.
- Blocked genres affect discovery and playlist/Jam recommendations, but not catalog search or
  save/review actions in `Músicas & Reviews`. Age restrictions still apply there.
- Users younger than 18 are only allowed as dependent profiles in a Family plan.
- Premium-only capabilities are statistics (`/perfil/dash`), editing existing interactions,
  interaction history, and blocked-genre management.
- A Jam awards 1 point for a like and 2 for a superlike, subject to its configured superlike
  limit. Skip votes are unique per participant and current track; reaching the vote target
  advances the queue automatically. The host can end a Jam but cannot force-skip a track.
- Reviews can be deleted only by their author. Review likes are unique per user and review.
- User-controlled resource writes verify ownership before changing playlists, reviews, or Jam
  membership.

## Layer boundaries

- `app/domain/` contains framework-independent dataclasses and ABC ports only.
- `app/application/` contains use cases, business rules, constants, and application exceptions.
- `app/infrastructure/` contains SQLAlchemy models, repositories, migrations, security, and
  external-service adapters.
- `app/presentation/` contains Pydantic schemas, HTTP routers, and dependency wiring.

## Persistence and external services

- Local default: SQLite at `ribbit_local.db`; production database is configured with
  `DATABASE_URL` (PostgreSQL).
- Startup creates missing tables and applies additive SQLite/PostgreSQL-compatible column
  migrations for the existing schema.
- iTunes is used to fill a missing preview URL and save it to the catalog. Spotify operations
  are mocked when credentials are unavailable.
