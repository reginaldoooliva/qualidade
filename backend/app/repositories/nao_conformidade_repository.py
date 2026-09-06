from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.nao_conformidade import ClassificacaoNC, NaoConformidade, OrigemNC, StatusNC
from app.models.plano_acao import PlanoDeAcao, StatusPlanoAcao


def _com_relacionamentos(stmt):
    return stmt.options(
        selectinload(NaoConformidade.peca),
        selectinload(NaoConformidade.etapa),
        selectinload(NaoConformidade.caracteristica),
        selectinload(NaoConformidade.responsavel_analise),
        selectinload(NaoConformidade.aberto_por),
        selectinload(NaoConformidade.planos_acao),
    )


def get_by_id(db: Session, nc_id: int) -> NaoConformidade | None:
    stmt = _com_relacionamentos(select(NaoConformidade).where(NaoConformidade.id == nc_id))
    return db.scalar(stmt)


def get_ultimo_numero_do_ano(db: Session, prefixo: str) -> str | None:
    stmt = (
        select(NaoConformidade.numero_rnc)
        .where(NaoConformidade.numero_rnc.like(f"{prefixo}%"))
        .order_by(NaoConformidade.numero_rnc.desc())
        .limit(1)
    )
    return db.scalar(stmt)


def list_nc(
    db: Session,
    status: StatusNC | None = None,
    peca_id: int | None = None,
    classificacao: ClassificacaoNC | None = None,
    origem: OrigemNC | None = None,
    responsavel_analise_id: int | None = None,
    com_plano: bool | None = None,
    data_inicio: date | None = None,
    data_fim: date | None = None,
) -> list[NaoConformidade]:
    stmt = _com_relacionamentos(select(NaoConformidade))
    if status is not None:
        stmt = stmt.where(NaoConformidade.status == status)
    if peca_id is not None:
        stmt = stmt.where(NaoConformidade.peca_id == peca_id)
    if classificacao is not None:
        stmt = stmt.where(NaoConformidade.classificacao == classificacao)
    if origem is not None:
        stmt = stmt.where(NaoConformidade.origem == origem)
    if responsavel_analise_id is not None:
        stmt = stmt.where(NaoConformidade.responsavel_analise_id == responsavel_analise_id)
    if data_inicio is not None:
        stmt = stmt.where(NaoConformidade.data_abertura >= datetime.combine(data_inicio, datetime.min.time()))
    if data_fim is not None:
        stmt = stmt.where(NaoConformidade.data_abertura <= datetime.combine(data_fim, datetime.max.time()))
    stmt = stmt.order_by(NaoConformidade.id.desc())

    resultado = list(db.scalars(stmt))
    if com_plano is not None:
        resultado = [nc for nc in resultado if (len(nc.planos_acao) > 0) == com_plano]
    return resultado


def create(db: Session, nc: NaoConformidade) -> NaoConformidade:
    db.add(nc)
    db.commit()
    db.refresh(nc)
    return get_by_id(db, nc.id)


def update(db: Session, nc: NaoConformidade) -> NaoConformidade:
    db.commit()
    db.refresh(nc)
    return nc


def indicadores(db: Session) -> dict:
    hoje = date.today()
    inicio_mes = hoje.replace(day=1)
    todas = list(db.scalars(select(NaoConformidade)))
    planos_abertos = list(
        db.scalars(select(PlanoDeAcao).where(PlanoDeAcao.status != StatusPlanoAcao.ENCERRADO))
    )
    acoes_atrasadas = sum(
        1
        for plano in planos_abertos
        for acao in plano.acoes_corretivas
        if acao.status_calculado == "atrasada"
    )
    return {
        "abertas": sum(1 for nc in todas if nc.status == StatusNC.ABERTA),
        "em_analise": sum(1 for nc in todas if nc.status == StatusNC.EM_ANALISE),
        "em_tratamento": sum(1 for nc in todas if nc.status == StatusNC.EM_TRATAMENTO),
        "encerradas_no_mes": sum(
            1
            for nc in todas
            if nc.status == StatusNC.ENCERRADA
            and nc.data_encerramento is not None
            and nc.data_encerramento.date() >= inicio_mes
        ),
        "com_plano_aberto": sum(1 for nc in todas if nc.tem_plano_aberto),
        "acoes_atrasadas": acoes_atrasadas,
    }
