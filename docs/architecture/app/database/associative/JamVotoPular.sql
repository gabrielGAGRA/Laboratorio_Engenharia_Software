-- Votação democrática para pular a música em reprodução (um voto por participante)
CREATE TABLE jam_votos_pular (
    jam_fila_id INT NOT NULL,
    jam_id INT NOT NULL,
    usuario_id INT NOT NULL,
    criado_em TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (jam_fila_id, usuario_id),
    CONSTRAINT fk_jam_votos_pular_fila
        FOREIGN KEY (jam_fila_id, jam_id) REFERENCES jam_fila (jam_fila_id, jam_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_jam_votos_pular_participante
        FOREIGN KEY (jam_id, usuario_id) REFERENCES jam_participantes (jam_id, usuario_id)
        ON DELETE CASCADE
);

CREATE INDEX idx_jam_votos_pular_participante ON jam_votos_pular (jam_id, usuario_id);
