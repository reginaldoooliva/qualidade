from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.fornecedor import Fornecedor


def get_by_id(db: Session, fornecedor_id: int) -> Fornecedor | None:
    return db.get(Fornecedor, fornecedor_id)


def get_by_codigo(db: Session, codigo: str) -> Fornecedor | None:
    return db.scalar(select(Fornecedor).where(Fornecedor.codigo == codigo))


def list_fornecedores(db: Session, busca: str | None = None) -> list[Fornecedor]:
    stmt = select(Fornecedor)
    if busca:
        termo = f"%{busca}%"
        stmt = stmt.where((Fornecedor.codigo.ilike(termo)) | (Fornecedor.nome.ilike(termo)))
    stmt = stmt.order_by(Fornecedor.codigo)
    return list(db.scalars(stmt))


def create(db: Session, fornecedor: Fornecedor) -> Fornecedor:
    db.add(fornecedor)
    db.commit()
    db.refresh(fornecedor)
    return fornecedor


def update(db: Session, fornecedor: Fornecedor) -> Fornecedor:
    db.commit()
    db.refresh(fornecedor)
    return fornecedor
