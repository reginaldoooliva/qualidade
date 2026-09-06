from datetime import date, datetime, time

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.coleta import Medicao, RodadaColeta
from app.models.peca import Caracteristica, Etapa
from app.models.producao import OrdemProducao


def list_medicoes_peca(
    db: Session,
    peca_id: int,
    etapa_id: int | None = None,
    data_inicio: date | None = None,
    data_fim: date | None = None,
    operador_id: int | None = None,
) -> list[Medicao]:
    stmt = (
        select(Medicao)
        .join(RodadaColeta, RodadaColeta.id == Medicao.rodada_id)
        .join(OrdemProducao, OrdemProducao.id == RodadaColeta.ordem_id)
        .join(Etapa, Etapa.id == RodadaColeta.etapa_id)
        .join(Caracteristica, Caracteristica.id == Medicao.caracteristica_id)
        .where(OrdemProducao.peca_id == peca_id)
        .options(
            selectinload(Medicao.rodada).selectinload(RodadaColeta.ordem),
            selectinload(Medicao.rodada).selectinload(RodadaColeta.etapa),
            selectinload(Medicao.caracteristica),
            selectinload(Medicao.operador),
        )
        .order_by(Medicao.data_hora)
    )
    if etapa_id is not None:
        stmt = stmt.where(RodadaColeta.etapa_id == etapa_id)
    if operador_id is not None:
        stmt = stmt.where(Medicao.operador_id == operador_id)
    if data_inicio is not None:
        stmt = stmt.where(Medicao.data_hora >= datetime.combine(data_inicio, time.min))
    if data_fim is not None:
        stmt = stmt.where(Medicao.data_hora <= datetime.combine(data_fim, time.max))
    return list(db.scalars(stmt))
