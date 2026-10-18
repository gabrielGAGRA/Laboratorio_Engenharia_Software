"""Small additive schema migrations for installations without Alembic yet."""

from sqlalchemy import Engine, inspect

_ADDITIVE_COLUMNS = {
    "usuarios": {"data_nascimento": "DATE"},
    "playlists": {
        "duracao_maxima_segundos": "INTEGER",
        "filtros_deck": "TEXT",
    },
    "jams": {
        "duracao_minutos": "INTEGER NOT NULL DEFAULT 60",
        "limite_superlikes": "INTEGER NOT NULL DEFAULT 10",
        "superlikes_usados": "INTEGER NOT NULL DEFAULT 0",
        "meta_votos_pular": "INTEGER NOT NULL DEFAULT 3",
        "duracao_acumulada_segundos": "INTEGER NOT NULL DEFAULT 0",
        "fonte_deck": "VARCHAR(32) NOT NULL DEFAULT 'livre'",
        "playlist_origem_id": "INTEGER",
    },
}


def migrar_colunas_aditivas(engine: Engine) -> None:
    """Additive, repeatable migration preserving existing user and playlist data."""
    inspector = inspect(engine)
    with engine.begin() as connection:
        for table, columns in _ADDITIVE_COLUMNS.items():
            existentes = {coluna["name"] for coluna in inspector.get_columns(table)}
            for coluna, tipo in columns.items():
                if coluna not in existentes:
                    connection.exec_driver_sql(
                        f"ALTER TABLE {table} ADD COLUMN {coluna} {tipo}"
                    )
