# TODO — Ribbit

Itens abertos e dívidas técnicas conhecidas. Atualize esta lista ao deferir algo.

---

## Backend — V0 (MVP Local)

- **Alembic**: O startup aplica migrações aditivas simples, mas ainda não há histórico versionado de schema. Adotar Alembic antes de evoluir o schema de produção.
- **PostgreSQL em produção**: `DATABASE_URL` usa SQLite local por padrão. Provisionar PostgreSQL e configurar a variável no ambiente de deploy.
- **Integração Spotify**: Exportação continua mockada/preparatória; implementar OAuth e exportação real antes de habilitar a integração.
- **Rate limiting**: Nenhum throttle nos endpoints. Adicionar rate limiting para autenticação e descoberta antes de exposição pública.
- **Cobertura**: Além dos fluxos E2E, os testes unitários agora cobrem regras de reviews, relatório de audiência/receita admin e filtros etários, de gêneros bloqueados e de músicas rejeitadas nos decks de playlist e Jam.
- **Seed local**: Contém planos, músicas de amostra e administrador local; é desabilitado com `RIBBIT_ENV=production`.

---

## Backend — Funcionalidades Futuras

- **Deck de amigo na Jam**: Envio direto de superlikes para o deck de outro participante não está modelado na V0. Definir tabela e use case quando a feature for detalhada.
- **Perfis infantis sem credenciais próprias**: Dependentes do plano Família possuem atualmente sua própria conta; perfis sem e-mail/senha não estão modelados.
- **Playlists contextuais avançadas**: Filtros por localização, clima e atividade específica (treino, estudo) planejados mas não implementados.
- **Desfazer interação (Undo swipe)**: Botão de desfazer da última faixa avaliada está na especificação de UI mas sem rota no backend.
- **WebSocket para Jams**: `obter_estado_e_checar_progresso` é hoje um endpoint REST com polling. Migrar para WebSocket para UX em tempo real.

---

## Frontend (Angular — `view/`)

- Diretório `view/` criado mas vazio. Todo o frontend Angular ainda está por ser desenvolvido.
- Consultar `docs/llm/view/` para guias de estilo TypeScript e Angular.

---

## Infraestrutura / Deploy

- Sem Dockerfile, CI/CD ou configuração de deploy. Definir quando o projeto sair do ambiente universitário local.
- Schema: a ordem de execução dos `.sql` importa (base/Funcoes primeiro, depois base, identity, resources, associative); usar Alembic para eliminar essa dependência manual.
