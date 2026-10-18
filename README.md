# Ribbit
<img width="300" height="300" alt="image" src="https://github.com/user-attachments/assets/3195384c-1bf5-4b72-8710-29e3af00807e" />


### Time: Crazy Frogs
- Carolina Britto Haddad
- Fernando Mendes Seraco
- Gabriel Agra de Castro Motta
- Mateus Silva de Araújo

## Sumário
- [Sobre](#-sobre)
- [Funcionalidades](#-funcionalidades)
  - [Aplicativo](#aplicativo)
  - [Painel Administrativo](#painel-administrativo)
- [Arquitetura e Tecnologias](#-arquitetura-e-tecnologias)
- [Como Executar](#-como-executar)

---

## Sobre

O **Ribbit** redefine a experiência de ouvir novas músicas através de uma mecânica interativa inspirada em *swipe*, usando da geração dinâmica de playlists e sessões colaborativas em tempo real (*Jams*).

O projeto é composto por duas frentes:
1. **Ribbit**: Aplicativo voltado ao usuário final para descoberta, criação de playlists inteligentes e interação social em grupo.
2. **Ribbit Admin Console**: Painel web restrito para curadoria de catálogo com *soft delete* e monitoramento de métricas.

---

## Funcionalidades

### Aplicativo 

#### 1. Onboarding e Preferências
- Cadastro completo de usuários com validação de dados.
- Seleção personalizada de gêneros e artistas favoritos para alimentar as recomendações.
- Bloqueio de gêneros musicais indesejados, impedindo que faixas associadas exclusivamente a eles apareçam nas Descobertas e Playlists.

#### 2. Descoberta por Swipe
- Feed central de novas faixas que descarta músicas já avaliadas ou gêneros bloqueados.
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
- Sistema de pontuação coletiva por swipe: Like (+1), Deslike (0) e Superlike (+1 com destaque de prioridade).
- Envio direto de faixas supercurtidas para o *deck* de um amigo participante.
- Votação democrática para pular músicas da fila em reprodução.
- Acompanhamento do tempo total e restante com margem de tolerância de $\pm 1$ minuto.

#### 5. Busca, Comunidade e Lançamentos
- Busca universal por faixa, artista, álbum ou gênero.
- Feed com suporte à avaliação imediata.
- Publicação, edição e exclusão de comentários e avaliações comunitárias em cada música.

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

- **Frontend**: TypeScript e Angular.
- **Backend**: Python.

---


## Como Executar

### Pré-requisitos

### 1. Instalar dependências

uv sync

### 2. Configurar variáveis de ambiente


### 3. Subir o servidor

uv run uvicorn app.main:app --reload

Acesse a documentação interativa em: **http://localhost:8000/docs**

### 4. Rodar os testes

```
uv run pytest
```

### 5. Quality gate

```
uv run ruff format;
uv run ruff check --fix;
uv run zuban check;
```
