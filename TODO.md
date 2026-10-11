# TODO

- Schema (docs/architecture/app/database): "deck" de amigo na Jam (envio direto de superlikes para outro participante) não está modelado; definir tabela quando a feature for detalhada.
- Schema: playlists por filtros contextuais (local, vibe, época, atividade) e perfis infantis sem e-mail/senha foram deixados fora do MVP.
- Schema: a ordem de execução dos .sql importa (base/Funcoes primeiro, depois base, identity, resources, associative); definir ferramenta de migration quando o backend existir. Requer PostgreSQL 15+ (`ON DELETE SET NULL (coluna)`).
