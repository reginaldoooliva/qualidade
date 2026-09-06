from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.nao_conformidade import NaoConformidade
from app.models.plano_acao import (
    AcaoCorretiva,
    CausaRaiz5Porques,
    CausaRaizIshikawa,
    PlanoDeAcao,
    StatusPlanoAcao,
    VerificacaoEficaciaPlano,
)


def _com_relacionamentos(stmt):
    return stmt.options(
        selectinload(PlanoDeAcao.acoes_corretivas).selectinload(AcaoCorretiva.responsavel),
        selectinload(PlanoDeAcao.causas_ishikawa),
        selectinload(PlanoDeAcao.causas_5porques),
        selectinload(PlanoDeAcao.verificacoes).selectinload(VerificacaoEficaciaPlano.responsavel),
        selectinload(PlanoDeAcao.nao_conformidade).selectinload(NaoConformidade.peca),
    )


def get_by_id(db: Session, plano_id: int) -> PlanoDeAcao | None:
    stmt = _com_relacionamentos(select(PlanoDeAcao).where(PlanoDeAcao.id == plano_id))
    return db.scalar(stmt)


def get_ativo_por_nc(db: Session, nc_id: int) -> PlanoDeAcao | None:
    stmt = _com_relacionamentos(
        select(PlanoDeAcao).where(PlanoDeAcao.nc_id == nc_id, PlanoDeAcao.status != StatusPlanoAcao.ENCERRADO)
    )
    return db.scalar(stmt)


def list_planos(db: Session, status: StatusPlanoAcao | None = None) -> list[PlanoDeAcao]:
    stmt = _com_relacionamentos(select(PlanoDeAcao))
    if status is not None:
        stmt = stmt.where(PlanoDeAcao.status == status)
    stmt = stmt.order_by(PlanoDeAcao.id.desc())
    return list(db.scalars(stmt))


def indicadores(db: Session) -> dict:
    hoje = date.today()
    inicio_mes = hoje.replace(day=1)
    todos = list(db.scalars(_com_relacionamentos(select(PlanoDeAcao))))
    ativos = [p for p in todos if p.status != StatusPlanoAcao.ENCERRADO]

    planos_atrasados = 0
    acoes_atrasadas = 0
    for plano in ativos:
        tem_atraso = False
        for acao in plano.acoes_ciclo_atual:
            if acao.status_calculado == "atrasada":
                acoes_atrasadas += 1
                tem_atraso = True
        if tem_atraso:
            planos_atrasados += 1

    return {
        "total_ativos": len(ativos),
        "aguardando_verificacao": sum(1 for p in ativos if p.status == StatusPlanoAcao.AGUARDANDO_VERIFICACAO),
        "planos_atrasados": planos_atrasados,
        "acoes_atrasadas": acoes_atrasadas,
        "encerrados_no_mes": sum(
            1
            for p in todos
            if p.status == StatusPlanoAcao.ENCERRADO and p.atualizado_em.date() >= inicio_mes
        ),
    }


def create(db: Session, plano: PlanoDeAcao) -> PlanoDeAcao:
    db.add(plano)
    db.commit()
    db.refresh(plano)
    return get_by_id(db, plano.id)


def update(db: Session, plano: PlanoDeAcao) -> PlanoDeAcao:
    db.commit()
    db.refresh(plano)
    return plano


def add_causa_ishikawa(db: Session, causa: CausaRaizIshikawa) -> CausaRaizIshikawa:
    db.add(causa)
    db.commit()
    db.refresh(causa)
    return causa


def get_causa_ishikawa(db: Session, plano_id: int, causa_id: int) -> CausaRaizIshikawa | None:
    stmt = select(CausaRaizIshikawa).where(
        CausaRaizIshikawa.id == causa_id, CausaRaizIshikawa.plano_id == plano_id
    )
    return db.scalar(stmt)


def update_causa_ishikawa(db: Session, causa: CausaRaizIshikawa) -> CausaRaizIshikawa:
    db.commit()
    db.refresh(causa)
    return causa


def delete_causa_ishikawa(db: Session, causa: CausaRaizIshikawa) -> None:
    db.delete(causa)
    db.commit()


def get_causa_5porques_por_nivel(db: Session, plano_id: int, nivel: int) -> CausaRaiz5Porques | None:
    stmt = select(CausaRaiz5Porques).where(
        CausaRaiz5Porques.plano_id == plano_id, CausaRaiz5Porques.nivel == nivel
    )
    return db.scalar(stmt)


def upsert_causa_5porques(db: Session, causa: CausaRaiz5Porques) -> CausaRaiz5Porques:
    db.add(causa)
    db.commit()
    db.refresh(causa)
    return causa


def get_causa_5porques(db: Session, plano_id: int, causa_id: int) -> CausaRaiz5Porques | None:
    stmt = select(CausaRaiz5Porques).where(
        CausaRaiz5Porques.id == causa_id, CausaRaiz5Porques.plano_id == plano_id
    )
    return db.scalar(stmt)


def add_acao(db: Session, acao: AcaoCorretiva) -> AcaoCorretiva:
    db.add(acao)
    db.commit()
    db.refresh(acao)
    return acao


def get_acao(db: Session, plano_id: int, acao_id: int) -> AcaoCorretiva | None:
    stmt = select(AcaoCorretiva).where(AcaoCorretiva.id == acao_id, AcaoCorretiva.plano_id == plano_id)
    return db.scalar(stmt)


def update_acao(db: Session, acao: AcaoCorretiva) -> AcaoCorretiva:
    db.commit()
    db.refresh(acao)
    return acao


def add_verificacao(db: Session, verificacao: VerificacaoEficaciaPlano) -> VerificacaoEficaciaPlano:
    db.add(verificacao)
    db.commit()
    db.refresh(verificacao)
    return verificacao
