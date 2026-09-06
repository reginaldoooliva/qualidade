from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.peca import Caracteristica


def get_by_id(db: Session, caracteristica_id: int) -> Caracteristica | None:
    return db.get(Caracteristica, caracteristica_id)


def list_by_etapa(db: Session, etapa_id: int) -> list[Caracteristica]:
    stmt = select(Caracteristica).where(Caracteristica.etapa_id == etapa_id).order_by(Caracteristica.id)
    return list(db.scalars(stmt))


def create(db: Session, caracteristica: Caracteristica) -> Caracteristica:
    db.add(caracteristica)
    db.commit()
    db.refresh(caracteristica)
    return caracteristica


def update(db: Session, caracteristica: Caracteristica) -> Caracteristica:
    db.commit()
    db.refresh(caracteristica)
    return caracteristica
