---
trigger: model_decision
description: Use when editing app/ Python - package layout, hexagonal layers, composition root, and where adapters vs domain/application code belong.
globs: app/**/*.py
---

# Architecture

| Layer | Path | Key modules |
| --- | --- | --- |
| Presentation | `app/presentation/` | `schemas.py`, `dependencies.py`, `routers/auth.py`, `routers/descoberta.py`, `routers/playlists.py`, `routers/jams.py`, `routers/musicas_reviews.py`, `routers/perfil.py`, `routers/admin.py` |
| Application | `app/application/` | `auth_use_cases.py`, `descoberta_use_cases.py`, `playlist_use_cases.py`, `perfil_use_cases.py`, `jam_use_cases.py`, `review_use_cases.py`, `admin_use_cases.py` |
| Domain | `app/domain/` | `entities.py` (dataclasses puras), `ports.py` (ABCs de repositório e serviço externo), `exceptions.py` (hierarquia `CustomError`) |
| Infrastructure | `app/infrastructure/` | `database.py` (engine + `get_db`), `db_models.py` (9 modelos SQLAlchemy), `repositories.py` (7 repositórios concretos), `apis_externas.py` (Spotify + iTunes), `seed.py` |

**Composition root**: `app/main.py` — cria a app FastAPI, registra todos os routers via `app.include_router(...)` e executa `popular_dados_iniciais()` no evento `lifespan`.

**Toda persistência passa pelos ports** definidos em `app/domain/ports.py` e implementados em `app/infrastructure/repositories.py`. Nenhum use case importa SQLAlchemy diretamente.

Deeper package map: `docs/llm/app/architecture-guide.md`.