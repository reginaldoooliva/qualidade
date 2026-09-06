from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.peca import Etapa


def get_by_id(db: Session, etapa_id: int) -> Etapa | None:
    return db.get(Etapa, etapa_id)


def get_by_peca_e_numero(db: Session, peca_id: int, numero_etapa: int) -> Etapa | None:
    stmt = select(Etapa).where(Etapa.peca_id == peca_id, Etapa.numero_etapa == numero_etapa)
    return db.scalar(stmt)


def list_by_peca(db: Session, peca_id: int) -> list[Etapa]:
    stmt = select(Etapa).where(Etapa.peca_id == peca_id).order_by(Etapa.numero_etapa)
    return list(db.scalars(stmt))


def create(db: Session, etapa: Etapa) -> Etapa:
    db.add(etapa)
    db.commit()
    db.refresh(etapa)
    return etapa


def update(db: Session, etapa: Etapa) -> Etapa:
    db.commit()
    db.refresh(etapa)
    return etapa
