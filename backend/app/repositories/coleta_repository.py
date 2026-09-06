from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.coleta import Medicao, RodadaColeta, StatusRodada


def get_by_id(db: Session, rodada_id: int) -> RodadaColeta | None:
    stmt = (
        select(RodadaColeta)
        .where(RodadaColeta.id == rodada_id)
        .options(selectinload(RodadaColeta.medicoes).selectinload(Medicao.operador))
    )
    return db.scalar(stmt)


def get_em_andamento(db: Session, ordem_id: int, etapa_id: int) -> RodadaColeta | None:
    stmt = select(RodadaColeta).where(
        RodadaColeta.ordem_id == ordem_id,
        RodadaColeta.etapa_id == etapa_id,
        RodadaColeta.status == StatusRodada.EM_ANDAMENTO,
    )
    return db.scalar(stmt)


def get_finalizada(db: Session, ordem_id: int, etapa_id: int) -> RodadaColeta | None:
    stmt = select(RodadaColeta).where(
        RodadaColeta.ordem_id == ordem_id,
        RodadaColeta.etapa_id == etapa_id,
        RodadaColeta.status != StatusRodada.EM_ANDAMENTO,
    )
    return db.scalar(stmt)


def get_medicao(db: Session, rodada_id: int, caracteristica_id: int, amostra_numero: int) -> Medicao | None:
    stmt = select(Medicao).where(
        Medicao.rodada_id == rodada_id,
        Medicao.caracteristica_id == caracteristica_id,
        Medicao.amostra_numero == amostra_numero,
    )
    return db.scalar(stmt)


def create(db: Session, rodada: RodadaColeta) -> RodadaColeta:
    db.add(rodada)
    db.commit()
    db.refresh(rodada)
    return rodada


def update(db: Session, rodada: RodadaColeta) -> RodadaColeta:
    db.commit()
    db.refresh(rodada)
    return rodada


def delete_medicao(db: Session, medicao: Medicao) -> None:
    db.delete(medicao)
    db.commit()
