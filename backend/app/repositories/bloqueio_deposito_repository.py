from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.bloqueio_deposito import BloqueioDeposito, StatusBloqueioDeposito


def _com_relacionamentos(stmt):
    return stmt.options(
        selectinload(BloqueioDeposito.peca),
        selectinload(BloqueioDeposito.criado_por),
        selectinload(BloqueioDeposito.liberado_por),
    )


def get_by_id(db: Session, bloqueio_id: int) -> BloqueioDeposito | None:
    stmt = _com_relacionamentos(select(BloqueioDeposito).where(BloqueioDeposito.id == bloqueio_id))
    return db.scalar(stmt)


def list_by_peca_id(db: Session, peca_id: int) -> list[BloqueioDeposito]:
    stmt = _com_relacionamentos(
        select(BloqueioDeposito).where(BloqueioDeposito.peca_id == peca_id).order_by(BloqueioDeposito.id.desc())
    )
    return list(db.scalars(stmt))


def list_all(
    db: Session, status: StatusBloqueioDeposito | None = None, busca: str | None = None
) -> list[BloqueioDeposito]:
    stmt = _com_relacionamentos(select(BloqueioDeposito))
    if status is not None:
        stmt = stmt.where(BloqueioDeposito.status == status)
    if busca:
        from app.models.peca import Peca

        termo = f"%{busca}%"
        stmt = stmt.join(Peca, Peca.id == BloqueioDeposito.peca_id).where(
            (Peca.codigo.ilike(termo)) | (Peca.descricao.ilike(termo))
        )
    stmt = stmt.order_by(BloqueioDeposito.id.desc())
    return list(db.scalars(stmt))


def create(db: Session, bloqueio: BloqueioDeposito) -> BloqueioDeposito:
    db.add(bloqueio)
    db.commit()
    db.refresh(bloqueio)
    return get_by_id(db, bloqueio.id)


def update(db: Session, bloqueio: BloqueioDeposito) -> BloqueioDeposito:
    db.commit()
    db.refresh(bloqueio)
    return bloqueio
