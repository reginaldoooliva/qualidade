from collections.abc import Generator

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.exceptions import CredenciaisInvalidasError, NaoAutorizadoError
from app.core.permissions import Perfil
from app.core.security import decodificar_token
from app.database import SessionLocal
from app.models.usuario import Usuario
from app.services import auth_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login", auto_error=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: str | None = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> Usuario:
    if not token:
        raise CredenciaisInvalidasError("Não autenticado")
    try:
        payload = decodificar_token(token)
    except ValueError as exc:
        raise CredenciaisInvalidasError(str(exc)) from exc

    usuario = auth_service.usuario_atual_por_login(db, payload.get("sub", ""))
    if not usuario:
        raise CredenciaisInvalidasError("Usuário do token não existe mais")
    return usuario


def require_role(*perfis: Perfil):
    def _checar(usuario: Usuario = Depends(get_current_user)) -> Usuario:
        if usuario.perfil not in perfis:
            raise NaoAutorizadoError(
                f"Esta ação requer um dos perfis: {', '.join(p.value for p in perfis)}"
            )
        return usuario

    return _checar
