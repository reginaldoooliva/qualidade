from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.peca import Caracteristica, Etapa, Peca


def get_by_id(db: Session, peca_id: int) -> Peca | None:
    return db.get(Peca, peca_id)


def get_by_codigo(db: Session, codigo: str) -> Peca | None:
    return db.scalar(select(Peca).where(Peca.codigo == codigo))


def list_pecas(db: Session, busca: str | None = None, cliente: str | None = None) -> list[Peca]:
    stmt = select(Peca)
    if busca:
        termo = f"%{busca}%"
        stmt = stmt.where((Peca.codigo.ilike(termo)) | (Peca.descricao.ilike(termo)))
    if cliente:
        stmt = stmt.where(Peca.cliente == cliente)
    stmt = stmt.order_by(Peca.codigo)
    return list(db.scalars(stmt).unique())


def contar_caracteristicas(db: Session, peca_id: int) -> int:
    stmt = (
        select(func.count(Caracteristica.id))
        .join(Etapa, Etapa.id == Caracteristica.etapa_id)
        .where(Etapa.peca_id == peca_id)
    )
    return db.scalar(stmt) or 0


def create(db: Session, peca: Peca) -> Peca:
    db.add(peca)
    db.commit()
    db.refresh(peca)
    return peca


def update(db: Session, peca: Peca) -> Peca:
    db.commit()
    db.refresh(peca)
    return peca
