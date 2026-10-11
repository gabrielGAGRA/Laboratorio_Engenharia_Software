CREATE TABLE usuario_generos_bloqueados (
    usuario_id INT NOT NULL,
    genero_id INT NOT NULL,
    PRIMARY KEY (usuario_id, genero_id),
    CONSTRAINT fk_usuario_generos_bloqueados_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuarios (usuario_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_usuario_generos_bloqueados_genero
        FOREIGN KEY (genero_id) REFERENCES generos (genero_id)
        ON DELETE CASCADE
);

CREATE INDEX idx_usuario_generos_bloqueados_genero ON usuario_generos_bloqueados (genero_id);
