from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.usuario import StatusUsuario, Usuario


def get_by_login(db: Session, login: str) -> Usuario | None:
    return db.scalar(select(Usuario).where(Usuario.login == login))


def get_by_id(db: Session, usuario_id: int) -> Usuario | None:
    return db.get(Usuario, usuario_id)


def list_ativos(db: Session) -> list[Usuario]:
    stmt = select(Usuario).where(Usuario.status == StatusUsuario.ATIVO).order_by(Usuario.nome)
    return list(db.scalars(stmt))


def create(db: Session, usuario: Usuario) -> Usuario:
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario
