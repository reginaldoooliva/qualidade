from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.maquina import Maquina


def get_by_id(db: Session, maquina_id: int) -> Maquina | None:
    return db.get(Maquina, maquina_id)


def get_by_codigo(db: Session, codigo: str) -> Maquina | None:
    return db.scalar(select(Maquina).where(Maquina.codigo == codigo))


def list_maquinas(db: Session, busca: str | None = None) -> list[Maquina]:
    stmt = select(Maquina)
    if busca:
        termo = f"%{busca}%"
        stmt = stmt.where((Maquina.codigo.ilike(termo)) | (Maquina.descricao.ilike(termo)))
    stmt = stmt.order_by(Maquina.codigo)
    return list(db.scalars(stmt))


def create(db: Session, maquina: Maquina) -> Maquina:
    db.add(maquina)
    db.commit()
    db.refresh(maquina)
    return maquina


def update(db: Session, maquina: Maquina) -> Maquina:
    db.commit()
    db.refresh(maquina)
    return maquina
