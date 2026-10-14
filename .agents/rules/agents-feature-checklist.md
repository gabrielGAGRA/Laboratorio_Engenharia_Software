---
trigger: model_decision
description: Use when editing app/ Python - feature change checklist, post-change quality gate, and decision matrix.
globs: app/**/*.py
---

# Feature Change Checklist

## Decision Matrix
After finishing a task, evaluate downstream updates. Open a file ONLY when a trigger below matches.

| You Changed | Evaluate |
| --- | --- |
| `app/domain/` (entities, ports, exceptions) | Run `tests/test_domain.py`; update `docs/llm/app/domain-api-guide.md` se contratos mudaram |
| `app/application/` (use cases) | Run `tests/test_application.py` e `tests/test_e2e_flow.py`; verifique regras de negócio em `docs/llm/app/domain-api-guide.md` |
| `app/infrastructure/` (db_models, repositories, apis_externas) | Run `tests/test_infrastructure.py`; verifique mapeamento ORM↔entidade em `docs/llm/app/architecture-guide.md` |
| `app/presentation/` (routers, schemas) | Run `tests/test_e2e_flow.py`; atualize `docs/llm/app/domain-api-guide.md` §1 se rotas ou DTOs mudaram |
| Regra de domínio ou invariante de negócio | Run `tests/test_domain.py` + `tests/test_application.py`; atualize `docs/llm/app/domain-api-guide.md` §2 |
| Layout de pacotes ou fronteiras de camadas | Atualize `.agents/rules/project-architecture.md` e `docs/llm/app/architecture-guide.md` |
| Convenções de teste ou estrutura de `tests/` | Atualize `.agents/rules/project-tests.md` e `docs/llm/tests-guide.md` |
| Qualquer diff antes de entregar | Rode `ruff format && ruff check --fix && uv run pytest` |