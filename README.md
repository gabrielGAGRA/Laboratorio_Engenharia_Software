# Ribbit
<img width="300" height="300" alt="image" src="https://github.com/user-attachments/assets/3195384c-1bf5-4b72-8710-29e3af00807e" />


### Time: Crazy Frogs
Membros:
- Carolina Britto Haddad
- Fernando Mendes Seraco
- Gabriel Agra de Castro Motta
- Mateus Silva de Araújo

## Sumário
- [Sobre o Projeto](#-sobre-o-projeto)
- [Funcionalidades](#-funcionalidades)
  - [Aplicativo Mobile](#aplicativo-mobile)
  - [Painel Administrativo (Web)](#painel-administrativo-web)
- [Arquitetura e Tecnologias](#-arquitetura-e-tecnologias)
- [Estrutura de Pastas](#-estrutura-de-pastas)
- [Como Executar](#-como-executar)

---

## Sobre o Projeto

O **Ribbit** redefine a experiência de encontrar novas músicas através de uma mecânica interativa inspirada em cartões de *swipe*, aliando geração dinâmica de playlists, sessões colaborativas em tempo real (*Jams*) e controle rígido de privacidade musical. 

O projeto é composto por duas frentes:
1. **Ribbit**: Aplicativo voltado ao usuário final para descoberta, criação de playlists inteligentes e interação social em grupo.
2. **Ribbit Admin Console**: Painel web restrito para curadoria de catálogo com *Soft Delete* e monitoramento de métricas financeiras.

---

## Funcionalidades

### Aplicativo 

#### 1. Onboarding e Preferências
- Cadastro completo de usuários com validação de dados.
- Seleção personalizada de gêneros e artistas favoritos para alimentar as recomendações.
- Bloqueio de gêneros musicais indesejados, impedindo que faixas associadas exclusivamente a eles apareçam nas Descobertas e Playlists.

#### 2. Descoberta por Swipe
- Feed central de novas faixas que descarta músicas já avaliadas ou gêneros bloqueados.
- Faixas marcadas como inadequadas para menores são filtradas em descoberta, playlists e Jams.
- Avaliação gestual rápida:
  - **Like (Direita)**: Envia a música para as Curtidas.
  - **Superlike (Cima)**: Adiciona a faixa às Amadas e Curtidas em lista separada.
  - **Rejeitar (Esquerda)**: Remove a música de futuras recomendações e sugestões de playlists.
- **Desfazer Ação**: Botão para restaurar a última faixa avaliada em caso de toque acidental.

#### 3. Playlists Inteligentes e Contextuais
- **Montagem por Swipe**: Modo de adicionar músicas a uma playlist via gestos sem poluir a lista global de Curtidas.
- **Duração Exata**: Ajuste algorítmico da duração planejada com margem de erro máxima de $\pm 1$ minuto.
- **Momentos de Evento**: Criação de blocos com durações e gêneros distintos para eventos complexos.
- **Lineup de Festivais**: Geração de sugestões baseada em múltiplos artistas informados.
- **Filtros Contextuais**: Playlists por localização/viagem, clima/vibe, época (década ou ano) e atividades específicas (treino, estudo).
- **Modo Referência**: Geração automática com base em Curtidas, Amadas ou playlists prévias.

#### 4. Jams Colaborativas
- Criação de salas em grupo com convite para amigos.
- Sistema de pontuação coletiva por swipe: Like (+1) e Superlike (+2), sujeito ao limite da sala.
- Sugestões da fila conforme a fonte configurada para a sala.
- A fila avança automaticamente quando a meta de votos únicos para pular a faixa é atingida; o host pode encerrar a sala.
- Acompanhamento do tempo total e restante com margem de tolerância de $\pm 1$ minuto.

#### 5. Busca, Comunidade e Lançamentos
- Busca universal por faixa, artista, álbum ou gênero.
- Feed com suporte à avaliação imediata.
- Publicação e exclusão pelo autor de comentários e avaliações comunitárias em cada música.

#### 6. Perfil e Dados
- Gestão e edição de listas de Curtidas, Amadas, Rejeitadas e Artistas favoritos.
- Dashboard pessoal com artistas principais, gêneros predominantes, entre outras estatísticas.
- Exclusão transparente de dados sob solicitação do usuário.
- Edição do plano de assinatura


---

### Painel Administrativo (Web)

#### 1. Gestão de Catálogo & Soft Delete 
- Acesso seguro exclusivo para contas com permissão de administrador.
- Formulário de cadastro com metadados completos (título, artista, gênero) e upload de arquivos de áudio.
- **Soft Delete de Conteúdo**: Ao remover uma faixa, ela é ocultada das buscas públicas e das descobertas, permanecendo registrada nos históricos de reprodução dos usuários para integridade de dados e auditoria.

#### 2. Dashboard Executivo e Cálculo de Receita
- Visualização de acessos agrupados por conteúdo e por categoria/gênero.
- Contagem dinâmica de usuários ativos sincronizada com a base.
- Cálculo da Receita Líquida da plataforma


---


## Arquitetura e Tecnologias

- **Frontend**: TypeScript e Angular (Framework).
- **Backend**: Python -- FastAPI.

---

## Estrutura de Pastas

```
Laboratorio_Engenharia_Software/
├── app/
│   ├── main.py                        # Bootstrap FastAPI + lifespan (seed + routers)
│   ├── domain/                        # Camada de Domínio — Python puro
│   │   ├── entities.py                # Dataclasses: Plano, Usuario, Musica, Interacao, Playlist, Jam, etc.
│   │   ├── ports.py                   # ABCs: repositórios e serviço externo de música
│   ├── application/                   # Casos de Uso — orquestração pura
│   │   ├── auth_use_cases.py
│   │   ├── descoberta_use_cases.py
│   │   ├── playlist_use_cases.py
│   │   ├── perfil_use_cases.py
│   │   ├── jam_use_cases.py
│   │   ├── review_use_cases.py
│   │   ├── admin_use_cases.py
│   │   ├── constants.py              # Constantes e regras compartilhadas
│   │   └── exceptions.py             # Erros da camada de aplicação
│   ├── infrastructure/                # Adaptadores de I/O
│   │   ├── database.py               # Engine SQLAlchemy + get_db()
│   │   ├── db_models.py              # Modelos ORM
│   │   ├── repositories.py           # Implementações concretas dos ports
│   │   ├── apis_externas.py          # Adaptadores Spotify + iTunes
│   │   ├── migrations.py             # Migrações aditivas de schema
│   │   ├── security.py               # Tokens Bearer assinados
│   │   └── seed.py                   # Dados iniciais e administrador local
│   └── presentation/                  # Camada HTTP
│       ├── schemas.py                 # DTOs Pydantic v2
│       ├── dependencies.py            # Injeção de dependência (DI)
│       └── routers/
│           ├── auth.py               # POST /api/auth/cadastrar, /login
│           ├── descoberta.py         # GET /api/descoberta/proxima, POST /interagir
│           ├── playlists.py          # CRUD de playlists + exportação Spotify
│           ├── jams.py               # Criação e votação de Jams colaborativas
│           ├── musicas_reviews.py    # Busca de músicas + reviews da comunidade
│           ├── perfil.py             # Perfil, planos, família e estatísticas Premium
│           └── admin.py              # Rotas administrativas protegidas por token/role
├── tests/
│   ├── test_domain.py
│   ├── test_infrastructure.py
│   ├── test_application.py
│   └── test_e2e_flow.py
├── docs/
│   ├── architecture/app/database/    # Esquemas SQL auxiliares
│   └── llm/app/                      # Guias para IAs: arquitetura, domínio, regras Python
├── .agents/                           # Regras e skills do agente de IA
├── pyproject.toml                     # Dependências e configuração Ruff/pytest
└── TODO.md                            # Itens abertos para próximas versões
```

## Como Executar

### Pré-requisitos

- Python 3.15 com [`uv`](https://docs.astral.sh/uv/) instalado
- (Opcional) PostgreSQL para produção; SQLite é usado localmente por padrão

### 1. Instalar dependências

```bash
uv sync
```

### 2. Configurar variáveis de ambiente (opcional)

Crie um `.env` na raiz ou exporte no shell:

```bash
# SQLite local (padrão — sem configuração necessária)
# DATABASE_URL=sqlite:///./ribbit_local.db

# PostgreSQL (produção)
# DATABASE_URL=postgresql://user:senha@localhost:5432/ribbit

# Integrações externas (opcional para V0)
# SPOTIFY_CLIENT_ID=...
# SPOTIFY_CLIENT_SECRET=...
# RIBBIT_SECRET_KEY=<segredo-aleatorio-persistente> 
# RIBBIT_ENV=production
# RIBBIT_ADMIN_EMAIL=admin@ribbit.example.com
# RIBBIT_ADMIN_PASSWORD=RibbitLocal2026!
```

### 3. Subir o servidor

```bash
uv run uvicorn app.main:app --reload
```

O banco SQLite (`ribbit_local.db`) e os dados de seed (3 planos, 5 músicas e um administrador
local) são criados automaticamente na primeira inicialização fora de produção. Entre como
`admin@ribbit.example.com` com a senha `RibbitLocal2026!`; configure `RIBBIT_SECRET_KEY` e
desative o seed local em produção.

Acesse a documentação interativa em: **http://localhost:8000/docs**

### 4. Rodar os testes

```bash
uv run pytest
```

### 5. Quality gate (lint + format)

```bash
uv run ruff format
uv run ruff check --fix
```
