CREATE TABLE avaliacao_curtidas (
    avaliacao_id INT NOT NULL,
    usuario_id INT NOT NULL,
    criado_em TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (avaliacao_id, usuario_id),
    CONSTRAINT fk_avaliacao_curtidas_avaliacao
        FOREIGN KEY (avaliacao_id) REFERENCES avaliacoes_comentarios (avaliacao_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_avaliacao_curtidas_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuarios (usuario_id)
        ON DELETE CASCADE
);

CREATE INDEX idx_avaliacao_curtidas_usuario ON avaliacao_curtidas (usuario_id);

-- Mantém avaliacoes_comentarios.likes_count consistente com as curtidas reais
CREATE FUNCTION atualiza_likes_count() RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE avaliacoes_comentarios SET likes_count = likes_count + 1 WHERE avaliacao_id = NEW.avaliacao_id;
    ELSE
        UPDATE avaliacoes_comentarios SET likes_count = likes_count - 1 WHERE avaliacao_id = OLD.avaliacao_id;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_avaliacao_curtidas_count
    AFTER INSERT OR DELETE ON avaliacao_curtidas
    FOR EACH ROW EXECUTE FUNCTION atualiza_likes_count();
