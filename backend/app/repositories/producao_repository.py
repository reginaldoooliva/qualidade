from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.producao import OrdemProducao


def get_by_peca_e_numero(db: Session, peca_id: int, numero_ordem: str) -> OrdemProducao | None:
    stmt = select(OrdemProducao).where(
        OrdemProducao.peca_id == peca_id, OrdemProducao.numero_ordem == numero_ordem
    )
    return db.scalar(stmt)


def get_by_id(db: Session, ordem_id: int) -> OrdemProducao | None:
    return db.get(OrdemProducao, ordem_id)


def create(db: Session, ordem: OrdemProducao) -> OrdemProducao:
    db.add(ordem)
    db.commit()
    db.refresh(ordem)
    return ordem
