"""Database seed script for default plans and sample songs."""

import os
from collections.abc import Callable

from sqlalchemy.orm import Session

from app.infrastructure.db_models import MusicaModel, PlanoModel, UsuarioModel


def run_seed(
    session: Session, hash_admin_password: Callable[[str], str] | None = None
) -> None:
    """Verifica e popula planos e músicas iniciais caso não existam."""
    # 1. Planos padrão
    planos_padrao = [
        {"nome": "Free", "preco_mensal": 0.00, "max_perfis": 1},
        {"nome": "Individual", "preco_mensal": 14.90, "max_perfis": 1},
        {"nome": "Família", "preco_mensal": 27.90, "max_perfis": 6},
    ]

    for p in planos_padrao:
        existente = (
            session.query(PlanoModel).filter(PlanoModel.nome == p["nome"]).first()
        )
        if not existente:
            session.add(
                PlanoModel(
                    nome=p["nome"],
                    preco_mensal=p["preco_mensal"],
                    max_perfis=p["max_perfis"],
                )
            )

    session.commit()

    if hash_admin_password:
        admin_email = os.getenv(
            "RIBBIT_ADMIN_EMAIL", "admin@ribbit.example.com"
        ).lower()
        admin_password = os.getenv("RIBBIT_ADMIN_PASSWORD", "RibbitLocal2026!")
        admin = (
            session.query(UsuarioModel)
            .filter(UsuarioModel.email == admin_email)
            .first()
        )
        if admin and not admin.is_admin:
            raise RuntimeError(
                f"A conta de seed {admin_email} existe sem papel administrativo."
            )
        if not admin:
            plano_free = (
                session.query(PlanoModel).filter(PlanoModel.nome == "Free").first()
            )
            if not plano_free:
                raise RuntimeError("Plano Free não encontrado para criar o admin.")
            session.add(
                UsuarioModel(
                    email=admin_email,
                    senha_hash=hash_admin_password(admin_password),
                    nome_exibicao="Administrador Local",
                    idade=30,
                    plano_id=plano_free.plano_id,
                    is_admin=True,
                )
            )
            session.commit()

    # 2. Músicas padrão de amostra
    musicas_padrao = [
        {
            "titulo": "Bohemian Rhapsody",
            "artista": "Queen",
            "album": "A Night at the Opera",
            "duracao_segundos": 354,
            "genero": "Rock",
            "pais": "Reino Unido",
            "ano_lancamento": 1975,
            "capa_url": "https://example.com/bohemian.jpg",
            "itunes_preview_url": "https://example.com/bohemian_preview.mp3",
            "bloqueado_para_menores": False,
        },
        {
            "titulo": "Shape of You",
            "artista": "Ed Sheeran",
            "album": "÷ (Divide)",
            "duracao_segundos": 233,
            "genero": "Pop",
            "pais": "Reino Unido",
            "ano_lancamento": 2017,
            "capa_url": "https://example.com/shapeofyou.jpg",
            "itunes_preview_url": "https://example.com/shapeofyou_preview.mp3",
            "bloqueado_para_menores": False,
        },
        {
            "titulo": "Rap God",
            "artista": "Eminem",
            "album": "The Marshall Mathers LP 2",
            "duracao_segundos": 363,
            "genero": "Hip Hop",
            "pais": "Estados Unidos",
            "ano_lancamento": 2013,
            "capa_url": "https://example.com/rapgod.jpg",
            "itunes_preview_url": "https://example.com/rapgod_preview.mp3",
            "bloqueado_para_menores": True,
        },
        {
            "titulo": "Blinding Lights",
            "artista": "The Weeknd",
            "album": "After Hours",
            "duracao_segundos": 200,
            "genero": "Pop",
            "pais": "Canadá",
            "ano_lancamento": 2020,
            "capa_url": "https://example.com/blindinglights.jpg",
            "itunes_preview_url": "https://example.com/blindinglights_preview.mp3",
            "bloqueado_para_menores": False,
        },
        {
            "titulo": "Smells Like Teen Spirit",
            "artista": "Nirvana",
            "album": "Nevermind",
            "duracao_segundos": 301,
            "genero": "Grunge",
            "pais": "Estados Unidos",
            "ano_lancamento": 1991,
            "capa_url": "https://example.com/nirvana.jpg",
            "itunes_preview_url": "https://example.com/nirvana_preview.mp3",
            "bloqueado_para_menores": False,
        },
    ]

    for m in musicas_padrao:
        existente = (
            session.query(MusicaModel)
            .filter(
                MusicaModel.titulo == m["titulo"],
                MusicaModel.artista == m["artista"],
            )
            .first()
        )
        if not existente:
            session.add(
                MusicaModel(
                    titulo=m["titulo"],
                    artista=m["artista"],
                    album=m["album"],
                    duracao_segundos=m["duracao_segundos"],
                    genero=m["genero"],
                    pais=m["pais"],
                    ano_lancamento=m["ano_lancamento"],
                    capa_url=m["capa_url"],
                    itunes_preview_url=m["itunes_preview_url"],
                    bloqueado_para_menores=m["bloqueado_para_menores"],
                    is_deleted=False,
                )
            )

    session.commit()
