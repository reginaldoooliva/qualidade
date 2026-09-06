from datetime import date, datetime, time

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.coleta import Medicao, RodadaColeta, StatusRodada
from app.models.producao import OrdemProducao
from app.models.usuario import Usuario


def list_rodadas_para_analise(
    db: Session,
    peca_id: int,
    etapa_id: int,
    rodada_id: int | None = None,
    data_inicio: date | None = None,
    data_fim: date | None = None,
) -> list[RodadaColeta]:
    stmt = (
        select(RodadaColeta)
        .join(OrdemProducao, OrdemProducao.id == RodadaColeta.ordem_id)
        .where(
            OrdemProducao.peca_id == peca_id,
            RodadaColeta.etapa_id == etapa_id,
            RodadaColeta.status != StatusRodada.EM_ANDAMENTO,
        )
    )
    if rodada_id is not None:
        stmt = stmt.where(RodadaColeta.id == rodada_id)
    if data_inicio is not None:
        stmt = stmt.where(RodadaColeta.data_hora_inicio >= datetime.combine(data_inicio, time.min))
    if data_fim is not None:
        stmt = stmt.where(RodadaColeta.data_hora_inicio <= datetime.combine(data_fim, time.max))
    stmt = stmt.order_by(RodadaColeta.data_hora_inicio)
    return list(db.scalars(stmt))


def list_medicoes(
    db: Session, rodada_ids: list[int], caracteristica_id: int, operador_id: int | None = None
) -> list[Medicao]:
    if not rodada_ids:
        return []
    stmt = select(Medicao).where(
        Medicao.rodada_id.in_(rodada_ids), Medicao.caracteristica_id == caracteristica_id
    )
    if operador_id is not None:
        stmt = stmt.where(Medicao.operador_id == operador_id)
    return list(db.scalars(stmt))


def list_operadores_das_rodadas(db: Session, rodada_ids: list[int]) -> list[Usuario]:
    if not rodada_ids:
        return []
    stmt = (
        select(Usuario)
        .join(Medicao, Medicao.operador_id == Usuario.id)
        .where(Medicao.rodada_id.in_(rodada_ids))
        .distinct()
        .order_by(Usuario.nome)
    )
    return list(db.scalars(stmt))
