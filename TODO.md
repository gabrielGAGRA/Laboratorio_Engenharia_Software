# TODO — Ribbit

---

## Backend

- ~~**Autenticação e Autorização Bearer/Token (§7 Auth Transport)**: A autenticação atual usa `usuario_id` fornecido pelo cliente e header `X-Admin-Id`. Substituir por autenticação segura com token Bearer (`Authorization: Bearer <token>`) resolvida via `Depends` com contexto de usuário autenticado e permissões, protegendo endpoints de perfil, exclusão de conta e moderação admin.~~ *(Concluído: implementado via `HMACTokenService` e dependências `require_user` / `require_admin`)*
- **PostgreSQL em produção**: `DATABASE_URL` default é SQLite local. Provisionar instância Postgres e configurar a variável de ambiente no ambiente de deploy.
- **Integração real Spotify/iTunes**: `app/infrastructure/apis_externas.py` tem os adaptadores estruturados, mas requer `SPOTIFY_CLIENT_ID` / `SPOTIFY_CLIENT_SECRET` reais. Testar fluxo OAuth de exportação de playlist.
- **Rate limiting**: Nenhum throttle nos endpoints. Adicionar middleware (ex: `slowapi`) especialmente em `/api/descoberta/proxima` e autenticação.

---

## Infraestrutura

- Sem Dockerfile, CI/CD ou configuração de deploy. Definir quando o projeto sair do ambiente universitário local.

---

## Funcionalidades Futuras

- **Deck de amigo na Jam**: Envio direto de superlikes para o deck de outro participante não está modelado na V0. Definir tabela e use case quando a feature for detalhada.
- **Perfis infantis**: Perfis sem e-mail/senha própria (dependentes sem conta Ribbit) ficaram fora do MVP.
- **Playlists contextuais avançadas**: Filtros por localização, clima e atividade específica (treino, estudo) planejados mas não implementados.
- **Desfazer interação (Undo swipe)**: Botão de desfazer da última faixa avaliada está na especificação de UI mas sem rota no backend.
- **WebSocket para Jams**: `obter_estado_e_checar_progresso` é hoje um endpoint REST com polling. Migrar para WebSocket para UX em tempo real.