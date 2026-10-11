CREATE TABLE musica_artistas (
    musica_id INT NOT NULL,
    artista_id INT NOT NULL,
    PRIMARY KEY (musica_id, artista_id),
    CONSTRAINT fk_musica_artistas_musica
        FOREIGN KEY (musica_id) REFERENCES musicas (musica_id)
        ON DELETE RESTRICT,
    CONSTRAINT fk_musica_artistas_artista
        FOREIGN KEY (artista_id) REFERENCES artistas (artista_id)
        ON DELETE RESTRICT
);

CREATE INDEX idx_musica_artistas_artista ON musica_artistas (artista_id);
