# AI Guide: Hexagonal Architecture and Package Layout

## Layer map

**Composition root — `app/main.py`**: creates the FastAPI application, registers routers,
initializes database tables and additive schema migrations, and loads development seed data.
The local seed is disabled when `RIBBIT_ENV=production`.

### Domain (`app/domain/`)

- `entities.py`: framework-independent dataclasses for plans, users, music, interactions,
  playlists, Jams, and reviews.
- `ports.py`: abstract repository and external-service contracts.
- This layer must not import SQLAlchemy, FastAPI, or Pydantic. Business exceptions and shared
  application constants are kept in `app/application/`.

### Application (`app/application/`)

Use cases depend on domain entities and ports, not on web or persistence frameworks.

- `auth_use_cases.py`: registration age gate, password hashing, and common user/admin login.
- `descoberta_use_cases.py`: unseen-track discovery with age and blocked-genre filters.
- `playlist_use_cases.py`: playlist ownership, deck generation, duration limits, track saving,
  and Spotify export orchestration.
- `perfil_use_cases.py`: plans, Premium permissions, profile management, and Family dependents.
- `jam_use_cases.py`: room creation/membership, queue scoring, superlike limits, unique skip
  votes, automatic advancement, and host termination.
- `review_use_cases.py`: search, song reviews, community feed, and review likes.
- `admin_use_cases.py`: admin-only audience, plan, administrator, and blocked-music operations.
- `constants.py`, `exceptions.py`: application-level invariants and errors mapped to HTTP by
  the composition root.

### Infrastructure (`app/infrastructure/`)

- `database.py`: SQLAlchemy engine and session dependency; SQLite foreign-key enforcement is
  enabled for local persistence.
- `db_models.py`: ORM tables, including Jam participants/votes and unique review likes.
- `repositories.py`: implementations of domain ports and ORM/domain conversions.
- `migrations.py`: additive column migrations for existing installations.
- `security.py`: signed expiring Bearer tokens.
- `apis_externas.py`: iTunes preview lookup and Spotify mock/preparation adapter.
- `seed.py`: idempotent local plans, sample catalog, and admin account.

### Presentation (`app/presentation/`)

- `schemas.py`: Pydantic request and response contracts.
- `dependencies.py`: dependency injection, Bearer identity resolution, and use case wiring.
- `routers/`: HTTP endpoints for authentication, discovery, playlists, Jams, reviews, profile,
  and administration. Routes derive user identity from the token, not from a client-provided
  `usuario_id`.

## Security and business boundaries

- Direct sign-up is limited to adults. Creating a minor is supported only for a Family-plan
  titular adding a dependent.
- Premium gates cover profile statistics, changing an existing interaction, categorized
  interaction history, and blocked-genre management.
- Admin operations require both a valid Bearer token and `is_admin == true`.
- Content filters for age and blocked genres apply consistently to discovery, playlist decks
  and additions, and Jam decks/queue interactions.
- Jam queue skipping is vote-driven only. The host may end the room but has no manual skip
  operation.
- Repositories enforce resource ownership where user-specific data is modified.

## Configuration and local execution

- `DATABASE_URL` selects the database; SQLite is the default and PostgreSQL is supported.
- `RIBBIT_SECRET_KEY` must be configured with a persistent random secret in production.
- `RIBBIT_ADMIN_EMAIL` and `RIBBIT_ADMIN_PASSWORD` override local development seed credentials.
- Run locally with `uv sync` and `uv run uvicorn app.main:app --reload`; run tests with
  `uv run pytest`.
