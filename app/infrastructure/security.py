"""Signed bearer token helpers for API authentication."""

import base64
import binascii
import hashlib
import hmac
import json
import os
import time
from functools import cache


@cache
def _development_signing_key() -> bytes:
    return os.urandom(32)


def _signing_key() -> bytes:
    configured = os.getenv("RIBBIT_SECRET_KEY")
    if configured:
        return configured.encode("utf-8")
    if os.getenv("RIBBIT_ENV", "development").lower() == "production":
        raise RuntimeError("RIBBIT_SECRET_KEY deve ser configurada em produção.")
    return _development_signing_key()


def validar_configuracao_seguranca() -> None:
    """Fail during startup when production token signing is not configured."""
    _signing_key()


def _encode_segment(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def criar_access_token(usuario_id: int, expiracao_segundos: int = 43_200) -> str:
    """Cria token assinado com validade limitada."""
    header = _encode_segment(b'{"alg":"HS256","typ":"JWT"}')
    payload = _encode_segment(
        json.dumps(
            {"sub": str(usuario_id), "exp": int(time.time()) + expiracao_segundos},
            separators=(",", ":"),
        ).encode("utf-8")
    )
    mensagem = f"{header}.{payload}".encode("ascii")
    assinatura = _encode_segment(
        hmac.new(_signing_key(), mensagem, hashlib.sha256).digest()
    )
    return f"{header}.{payload}.{assinatura}"


def _validar_claims_token(token: str) -> int:
    header, payload, assinatura = token.split(".")
    if header != _encode_segment(b'{"alg":"HS256","typ":"JWT"}'):
        raise ValueError("Token de acesso inválido.")
    mensagem = f"{header}.{payload}".encode("ascii")
    esperada = _encode_segment(
        hmac.new(_signing_key(), mensagem, hashlib.sha256).digest()
    )
    if not hmac.compare_digest(assinatura, esperada):
        raise ValueError("Token de acesso inválido.")
    dados = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
    usuario_id = int(dados["sub"])
    if int(dados["exp"]) <= int(time.time()):
        raise ValueError("Token de acesso expirado.")
    return usuario_id


def decodificar_access_token(token: str) -> int:
    """Valida assinatura e expiração e retorna o ID do usuário."""
    try:
        usuario_id = _validar_claims_token(token)
    except (
        ValueError,
        KeyError,
        TypeError,
        json.JSONDecodeError,
        binascii.Error,
        UnicodeDecodeError,
    ) as exc:
        raise ValueError("Token de acesso inválido.") from exc
    else:
        return usuario_id
