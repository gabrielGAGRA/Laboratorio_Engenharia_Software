---
trigger: model_decision
description: Use when editing Angular view code (src/**/*.ts, *.html) - TypeScript rules, lint/format/typecheck gate.
globs: src/**/*.{ts,html}
---

# View (Angular + TypeScript) Map

- Angular app lives in `src/`; the Python backend is `app/`. No hexagonal layering on the view.
- Tooling: `.oxlintrc.json` (oxlint type-aware, import, jsdoc), `eslint.config.mjs` (angular template linting), `tsconfig.json` (strict TypeScript 7), `.oxfmtrc.json` (oxfmt).
- Gate after every change: `npm run format`, `npm run lint:fix`, `npm run typecheck`.
- Only the judgement rules are written down; do not restate lint rules.

Deeper detail: `docs/llm/view/typescript-engineering-rules.md`, Angular conventions: `docs/llm/view/angular-style-guide.md`.
