from sqlalchemy.orm import Session

from app.core.exceptions import CredenciaisInvalidasError
from app.core.security import criar_access_token, verificar_senha
from app.models.usuario import StatusUsuario, Usuario
from app.repositories import usuario_repository
from app.schemas.auth import Token


def autenticar(db: Session, login: str, senha: str) -> Token:
    usuario = usuario_repository.get_by_login(db, login)
    if not usuario or not verificar_senha(senha, usuario.senha_hash):
        raise CredenciaisInvalidasError("Login ou senha inválidos")
    if usuario.status != StatusUsuario.ATIVO:
        raise CredenciaisInvalidasError("Usuário inativo")

    token = criar_access_token(subject=usuario.login, perfil=usuario.perfil.value)
    return Token(access_token=token, usuario=usuario)


def usuario_atual_por_login(db: Session, login: str) -> Usuario | None:
    return usuario_repository.get_by_login(db, login)
