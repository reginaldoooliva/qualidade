from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.departamento import Departamento


def get_by_id(db: Session, departamento_id: int) -> Departamento | None:
    return db.get(Departamento, departamento_id)


def get_by_nome(db: Session, nome: str) -> Departamento | None:
    return db.scalar(select(Departamento).where(Departamento.nome == nome))


def list_departamentos(db: Session, busca: str | None = None) -> list[Departamento]:
    stmt = select(Departamento)
    if busca:
        stmt = stmt.where(Departamento.nome.ilike(f"%{busca}%"))
    stmt = stmt.order_by(Departamento.nome)
    return list(db.scalars(stmt))


def create(db: Session, departamento: Departamento) -> Departamento:
    db.add(departamento)
    db.commit()
    db.refresh(departamento)
    return departamento


def update(db: Session, departamento: Departamento) -> Departamento:
    db.commit()
    db.refresh(departamento)
    return departamento
