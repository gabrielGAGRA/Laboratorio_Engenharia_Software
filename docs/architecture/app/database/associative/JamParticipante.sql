CREATE TABLE jam_participantes (
    jam_id INT NOT NULL,
    usuario_id INT NOT NULL,
    entrou_em TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (jam_id, usuario_id),
    CONSTRAINT fk_jam_participantes_jam
        FOREIGN KEY (jam_id) REFERENCES jams (jam_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_jam_participantes_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuarios (usuario_id)
        ON DELETE CASCADE
);

CREATE INDEX idx_jam_participantes_usuario ON jam_participantes (usuario_id);
