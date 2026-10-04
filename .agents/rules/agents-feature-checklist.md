---
trigger: model_decision
description: Use when editing app/ Python - feature change checklist, post-change quality gate, and decision matrix.
globs: app/**/*.py
---

<!-- TEMPLATE: Inject-ready rule. Replace every FILL block with target-repo facts; delete this banner when done. -->

# Feature Change Checklist

## Decision Matrix
After finishing a task, evaluate downstream updates. Open a file ONLY when a trigger below matches.
| You Changed | Evaluate |
| --- | --- |
<!-- FILL: Row — app/ behavior (domain, use cases, infra, HTTP). Discover: tests/ layer folders matching app/. Keep: matching test paths + run pytest for touched layer. -->
<!-- FILL: Row — HTTP request/response fields or router mapping. Discover: routers, schemas, tests/presentation/. Keep: docs/llm/domain-api-guide.md + presentation tests. -->
<!-- FILL: Row — domain invariant or validation rule. Discover: domain services, tests/domain/. Keep: docs/llm/domain-api-guide.md + matching domain tests. -->
<!-- FILL: Row — use-case orchestration or application port contract. Discover: use_cases/, tests/application/. Keep: project-domain-api or project-architecture guide + application tests. -->
<!-- FILL: Row — infrastructure adapter or external client. Discover: app/infrastructure/, tests/infrastructure/. Keep: project-architecture or project-domain-api guide + infra tests. -->
<!-- FILL: Row — structured logging or event enums. Discover: app/common/, log sites in routers/use cases. Keep: list concrete modules to review. -->
<!-- FILL: Row — layer map, adapters, composition root. Discover: app/ tree, http_bootstrap or wire_app. Keep: docs/llm/architecture-guide.md. -->
<!-- FILL: Row — pipeline, CloudFormation, Docker, or deploy config. Discover: pipeline/, CI yaml, README. Keep: list paths to review. -->
<!-- FILL: Row — test conventions or harness. Discover: tests/, pytest.ini. Keep: docs/llm/tests-guide.md + tests/pytest.ini. -->