CREATE TABLE musica_generos (
    musica_id INT NOT NULL,
    genero_id INT NOT NULL,
    PRIMARY KEY (musica_id, genero_id),
    CONSTRAINT fk_musica_generos_musica
        FOREIGN KEY (musica_id) REFERENCES musicas (musica_id)
        ON DELETE RESTRICT,
    CONSTRAINT fk_musica_generos_genero
        FOREIGN KEY (genero_id) REFERENCES generos (genero_id)
        ON DELETE RESTRICT
);

CREATE INDEX idx_musica_generos_genero ON musica_generos (genero_id);
