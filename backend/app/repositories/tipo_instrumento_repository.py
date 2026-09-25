from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.peca import StatusCadastro
from app.models.tipo_instrumento import TipoInstrumento


def get_by_id(db: Session, tipo_id: int) -> TipoInstrumento | None:
    return db.get(TipoInstrumento, tipo_id)


def get_by_nome(db: Session, nome: str) -> TipoInstrumento | None:
    return db.scalar(select(TipoInstrumento).where(TipoInstrumento.nome == nome))


def list_tipos(
    db: Session, busca: str | None = None, status: StatusCadastro | None = None
) -> list[TipoInstrumento]:
    stmt = select(TipoInstrumento)
    if busca:
        stmt = stmt.where(TipoInstrumento.nome.ilike(f"%{busca}%"))
    if status:
        stmt = stmt.where(TipoInstrumento.status == status)
    stmt = stmt.order_by(TipoInstrumento.nome)
    return list(db.scalars(stmt))


def create(db: Session, tipo: TipoInstrumento) -> TipoInstrumento:
    db.add(tipo)
    db.commit()
    db.refresh(tipo)
    return tipo


def update(db: Session, tipo: TipoInstrumento) -> TipoInstrumento:
    db.commit()
    db.refresh(tipo)
    return tipo
