---
trigger: model_decision
description: Use when writing or editing tests - test tree layout, fakes/mocks, pytest markers, and how to run unit vs integration suites.
globs: tests/**/*.py
---

# Tests

| Directory / File | Scope |
| --- | --- |
| `tests/test_domain.py` | Entidades e exceções do domínio puro (sem I/O) |
| `tests/test_infrastructure.py` | Repositórios concretos contra SQLite em memória (`sqlite:///:memory:`) |
| `tests/test_application.py` | Use cases com repositórios concretos em SQLite em memória (sem mocks) |
| `tests/test_e2e_flow.py` | Fluxo completo via `TestClient` do FastAPI (cadastro → login → swipe → playlist → perfil) |

**Doubles**: Os testes usam repositórios concretos (`app/infrastructure/repositories.py`) contra um banco SQLite em memória criado no setup de cada módulo de teste — sem mocks ou fakes separados. Isso garante que repositórios e use cases sejam testados juntos com schema real.

**Como rodar**:
```bash
uv run pytest                    # todos os testes
uv run pytest tests/test_domain.py   # camada específica
uv run pytest -v                 # verbose
```

Categories + isolation: `docs/llm/tests-guide.md` §5. TDD + CI policy: `docs/llm/software-engineering-rules.md` §9.