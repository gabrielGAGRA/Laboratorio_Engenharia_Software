-- Extensão para busca por similaridade (ILIKE / %) em títulos e nomes
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Mantém atualizado_em sincronizado em qualquer tabela que o possua
CREATE OR REPLACE FUNCTION set_atualizado_em() RETURNS TRIGGER AS $$
BEGIN
    NEW.atualizado_em = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
