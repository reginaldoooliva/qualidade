from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.nao_conformidade import AcaoDepartamental, NaoConformidade, StatusAcaoDepartamental


def get_by_id(db: Session, acao_id: int) -> AcaoDepartamental | None:
    return db.get(AcaoDepartamental, acao_id)


def create(db: Session, acao: AcaoDepartamental) -> AcaoDepartamental:
    db.add(acao)
    db.commit()
    db.refresh(acao)
    return acao


def update(db: Session, acao: AcaoDepartamental) -> AcaoDepartamental:
    db.commit()
    db.refresh(acao)
    return acao


def delete(db: Session, acao: AcaoDepartamental) -> None:
    db.delete(acao)
    db.commit()


def list_pendentes(db: Session, departamento_id: int | None = None) -> list[AcaoDepartamental]:
    stmt = (
        select(AcaoDepartamental)
        .where(AcaoDepartamental.status == StatusAcaoDepartamental.PENDENTE)
        .options(
            selectinload(AcaoDepartamental.nao_conformidade).selectinload(NaoConformidade.peca),
            selectinload(AcaoDepartamental.departamento),
            selectinload(AcaoDepartamental.criado_por),
            selectinload(AcaoDepartamental.concluido_por),
        )
        .order_by(AcaoDepartamental.criado_em)
    )
    if departamento_id is not None:
        stmt = stmt.where(AcaoDepartamental.departamento_id == departamento_id)
    return list(db.scalars(stmt))
