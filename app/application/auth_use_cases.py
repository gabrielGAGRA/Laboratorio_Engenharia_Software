"""Use cases for user authentication and administration access."""

import hashlib
import hmac
import os
from datetime import date

from app.application.exceptions import (
    BusinessRuleViolationError,
    DuplicateEntityError,
    EntityNotFoundError,
    ForbiddenError,
    UnauthorizedError,
)
from app.domain.entities import Usuario
from app.domain.ports import PlanoRepositoryPort, UsuarioRepositoryPort


def hash_password(password: str, salt: str | None = None) -> str:
    """Gera hash seguro com PBKDF2 HMAC-SHA256."""
    if not salt:
        salt = os.urandom(16).hex()
    hashed = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000
    ).hex()
    return f"{salt}${hashed}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verifica senha contra o hash armazenado."""
    if "$" not in stored_hash:
        return False
    salt, hashed = stored_hash.split("$", 1)
    recalculated = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000
    ).hex()
    return hmac.compare_digest(recalculated, hashed)


class AuthUseCases:
    """Casos de uso de autenticação e registro."""

    def __init__(
        self,
        usuario_repo: UsuarioRepositoryPort,
        plano_repo: PlanoRepositoryPort,
    ) -> None:
        self.usuario_repo = usuario_repo
        self.plano_repo = plano_repo

    def cadastrar_usuario(
        self,
        email: str,
        senha: str,
        nome_exibicao: str,
        idade: int | None = None,
        plano_id: int | None = None,
        data_nascimento: date | None = None,
    ) -> Usuario:
        """Registra novo usuário com validações de unicidade e plano."""
        email = email.strip().lower()
        existente = self.usuario_repo.buscar_por_email(email)
        if existente:
            raise DuplicateEntityError(f"E-mail {email} já está em uso.")

        if data_nascimento:
            hoje = date.today()
            if data_nascimento > hoje:
                raise BusinessRuleViolationError(
                    "Data de nascimento não pode estar no futuro."
                )
            idade = (
                hoje.year
                - data_nascimento.year
                - (
                    (hoje.month, hoje.day)
                    < (data_nascimento.month, data_nascimento.day)
                )
            )
        if idade is None or idade < 0:
            raise BusinessRuleViolationError("Data de nascimento inválida.")
        if Usuario.idade_indica_menor(idade):
            raise BusinessRuleViolationError(
                "Cadastro direto permitido apenas para maiores de 18 anos."
            )

        if plano_id is None:
            plano_free = self.plano_repo.buscar_por_nome("Free")
            if not plano_free or not plano_free.plano_id:
                raise EntityNotFoundError("Plano Free padrão não encontrado.")
            plano_id = plano_free.plano_id
        else:
            plano = self.plano_repo.buscar_por_id(plano_id)
            if not plano:
                raise EntityNotFoundError(f"Plano com ID {plano_id} não encontrado.")

        senha_hash = hash_password(senha)
        novo_usuario = Usuario(
            usuario_id=None,
            email=email,
            senha_hash=senha_hash,
            nome_exibicao=nome_exibicao.strip(),
            idade=idade,
            plano_id=plano_id,
            is_admin=False,
            data_nascimento=data_nascimento,
        )
        return self.usuario_repo.salvar(novo_usuario)

    def autenticar_usuario(self, email: str, senha: str) -> Usuario:
        """Autentica usuário por e-mail e senha."""
        usuario = self.usuario_repo.buscar_por_email(email)
        if not usuario:
            raise UnauthorizedError("Credenciais inválidas.")

        if not verify_password(senha, usuario.senha_hash):
            raise UnauthorizedError("Credenciais inválidas.")

        return usuario

    def login_admin(self, email: str, senha: str) -> Usuario:
        """Autentica e valida se o usuário possui permissão de administrador."""
        usuario = self.autenticar_usuario(email, senha)
        if not usuario.is_admin:
            raise ForbiddenError("Acesso restrito a administradores.")
        return usuario
