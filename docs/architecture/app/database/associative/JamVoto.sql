-- Swipe de um participante sobre um item da fila: like (+1), dislike (0), superlike (+1 e destaque)
CREATE TABLE jam_votos (
    jam_fila_id INT NOT NULL,
    jam_id INT NOT NULL,
    usuario_id INT NOT NULL,
    voto VARCHAR(10) NOT NULL,
    criado_em TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (jam_fila_id, usuario_id),
    -- FKs compostas: item da fila e votante precisam pertencer à mesma jam
    CONSTRAINT fk_jam_votos_fila
        FOREIGN KEY (jam_fila_id, jam_id) REFERENCES jam_fila (jam_fila_id, jam_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_jam_votos_participante
        FOREIGN KEY (jam_id, usuario_id) REFERENCES jam_participantes (jam_id, usuario_id)
        ON DELETE CASCADE,
    CONSTRAINT ck_jam_votos_voto CHECK (voto IN ('like', 'dislike', 'superlike'))
);

CREATE INDEX idx_jam_votos_participante ON jam_votos (jam_id, usuario_id);

-- Recalcula pontos e destaque do item a partir dos votos, evitando contador divergente
CREATE FUNCTION recalcula_jam_fila() RETURNS TRIGGER AS $$
DECLARE
    alvo INT := COALESCE(NEW.jam_fila_id, OLD.jam_fila_id);
BEGIN
    UPDATE jam_fila SET
        pontos_voto = (SELECT COUNT(*) FROM jam_votos WHERE jam_fila_id = alvo AND voto IN ('like', 'superlike')),
        is_destaque = EXISTS (SELECT 1 FROM jam_votos WHERE jam_fila_id = alvo AND voto = 'superlike')
    WHERE jam_fila_id = alvo;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_jam_votos_recalcula
    AFTER INSERT OR UPDATE OR DELETE ON jam_votos
    FOR EACH ROW EXECUTE FUNCTION recalcula_jam_fila();
