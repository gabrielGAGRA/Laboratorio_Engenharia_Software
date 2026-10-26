# TODO — Ribbit

Itens abertos e dívidas técnicas conhecidas. Atualize esta lista ao deferir algo.

---

## Backend — V0 (MVP Local)

- **JWT real**: Autenticação atual usa `X-Usuario-Id` / `X-Admin-Id` como headers de identidade (adequado para V0 universitário). 
- **Alembic**: Sem sistema de migração de banco. Criar configuração Alembic para gerenciar schema em PostgreSQL de produção.
- **PostgreSQL em produção**: `DATABASE_URL` default é SQLite local. Provisionar instância Postgres e configurar a variável de ambiente no ambiente de deploy.
- **Integração real Spotify/iTunes**: `app/infrastructure/apis_externas.py` tem os adaptadores estruturados, mas requer `SPOTIFY_CLIENT_ID` / `SPOTIFY_CLIENT_SECRET` reais. Testar fluxo OAuth de exportação de playlist.
- **Rate limiting**: Nenhum throttle nos endpoints. Adicionar middleware (ex: `slowapi`) especialmente em `/api/descoberta/proxima` e autenticação.
- **Testes de Jams, Reviews e Admin**: Cobertura atual concentrada em Auth, Descoberta, Playlist e Perfil. Adicionar testes unitários para `jam_use_cases.py`, `review_use_cases.py` e `admin_use_cases.py`.
- **`seed.py` temporário**: O script de seed com planos e músicas de amostra é exclusivo para desenvolvimento local. Remover do startup de produção quando houver dados reais.

---

## Backend — Funcionalidades Futuras

- **Deck de amigo na Jam**: Envio direto de superlikes para o deck de outro participante não está modelado na V0. Definir tabela e use case quando a feature for detalhada.
- **Perfis infantis**: Perfis sem e-mail/senha própria (dependentes sem conta Ribbit) ficaram fora do MVP.
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
