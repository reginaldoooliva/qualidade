from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.permissions import PERFIS_QUALIDADE
from app.deps import get_current_user, get_db, require_role
from app.models.plano_acao import StatusPlanoAcao
from app.models.usuario import Usuario
from app.schemas.plano_acao import (
    AcaoCorretivaCreate,
    Causa5PorquesUpsert,
    CausaIshikawaCreate,
    ConclusaoCausaRaizUpdate,
    IndicadoresPlanoAcao,
    MarcarRaizRequest,
    MetodologiaUpdate,
    PlanoDeAcaoDetalhe,
    PlanoDeAcaoListItem,
    VerificacaoEficaciaCreate,
)
from app.services import plano_acao_service

router = APIRouter(prefix="/planos-acao", tags=["planos-acao"])


@router.get("", response_model=list[PlanoDeAcaoListItem], dependencies=[Depends(get_current_user)])
def listar(status: StatusPlanoAcao | None = None, db: Session = Depends(get_db)):
    return [plano_acao_service.to_list_item(p) for p in plano_acao_service.listar(db, status=status)]


@router.get("/indicadores", response_model=IndicadoresPlanoAcao, dependencies=[Depends(get_current_user)])
def obter_indicadores(db: Session = Depends(get_db)):
    return plano_acao_service.indicadores(db)


@router.get("/{plano_id}", response_model=PlanoDeAcaoDetalhe, dependencies=[Depends(get_current_user)])
def obter(plano_id: int, db: Session = Depends(get_db)):
    return plano_acao_service.to_detalhe(db, plano_acao_service.obter(db, plano_id))


@router.patch("/{plano_id}/metodologia", response_model=PlanoDeAcaoDetalhe)
def trocar_metodologia(
    plano_id: int,
    dados: MetodologiaUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_role(*PERFIS_QUALIDADE)),
):
    plano = plano_acao_service.trocar_metodologia(db, plano_id, dados.metodologia_causa_raiz, usuario)
    return plano_acao_service.to_detalhe(db, plano)


@router.patch("/{plano_id}/conclusao-causa-raiz", response_model=PlanoDeAcaoDetalhe)
def atualizar_conclusao(
    plano_id: int,
    dados: ConclusaoCausaRaizUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_role(*PERFIS_QUALIDADE)),
):
    plano = plano_acao_service.atualizar_conclusao(db, plano_id, dados.conclusao_causa_raiz, usuario)
    return plano_acao_service.to_detalhe(db, plano)


@router.post("/{plano_id}/causas-ishikawa", response_model=PlanoDeAcaoDetalhe)
def adicionar_causa_ishikawa(
    plano_id: int,
    dados: CausaIshikawaCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_role(*PERFIS_QUALIDADE)),
):
    plano_acao_service.adicionar_causa_ishikawa(db, plano_id, dados, usuario)
    return plano_acao_service.to_detalhe(db, plano_acao_service.obter(db, plano_id))


@router.patch("/{plano_id}/causas-ishikawa/{causa_id}/marcar-raiz", response_model=PlanoDeAcaoDetalhe)
def marcar_causa_ishikawa(
    plano_id: int,
    causa_id: int,
    dados: MarcarRaizRequest,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_role(*PERFIS_QUALIDADE)),
):
    plano = plano_acao_service.marcar_causa_ishikawa(db, plano_id, causa_id, dados.marcada_como_raiz, usuario)
    return plano_acao_service.to_detalhe(db, plano)


@router.delete("/{plano_id}/causas-ishikawa/{causa_id}", status_code=204)
def remover_causa_ishikawa(
    plano_id: int,
    causa_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_role(*PERFIS_QUALIDADE)),
):
    plano_acao_service.remover_causa_ishikawa(db, plano_id, causa_id, usuario)


@router.put("/{plano_id}/causas-5porques", response_model=PlanoDeAcaoDetalhe)
def upsert_causa_5porques(
    plano_id: int,
    dados: Causa5PorquesUpsert,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_role(*PERFIS_QUALIDADE)),
):
    plano_acao_service.upsert_causa_5porques(db, plano_id, dados, usuario)
    return plano_acao_service.to_detalhe(db, plano_acao_service.obter(db, plano_id))


@router.patch("/{plano_id}/causas-5porques/{causa_id}/marcar-raiz", response_model=PlanoDeAcaoDetalhe)
def marcar_causa_5porques(
    plano_id: int,
    causa_id: int,
    dados: MarcarRaizRequest,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_role(*PERFIS_QUALIDADE)),
):
    plano = plano_acao_service.marcar_causa_5porques(db, plano_id, causa_id, dados.marcada_como_raiz, usuario)
    return plano_acao_service.to_detalhe(db, plano)


@router.post("/{plano_id}/acoes", response_model=PlanoDeAcaoDetalhe)
def adicionar_acao(
    plano_id: int,
    dados: AcaoCorretivaCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_role(*PERFIS_QUALIDADE)),
):
    plano = plano_acao_service.adicionar_acao(db, plano_id, dados, usuario)
    return plano_acao_service.to_detalhe(db, plano)


@router.patch("/{plano_id}/acoes/{acao_id}/concluir", response_model=PlanoDeAcaoDetalhe)
def concluir_acao(
    plano_id: int,
    acao_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_role(*PERFIS_QUALIDADE)),
):
    plano = plano_acao_service.concluir_acao(db, plano_id, acao_id, usuario)
    return plano_acao_service.to_detalhe(db, plano)


@router.post("/{plano_id}/avancar-verificacao", response_model=PlanoDeAcaoDetalhe)
def avancar_verificacao(
    plano_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_role(*PERFIS_QUALIDADE)),
):
    plano = plano_acao_service.avancar_verificacao(db, plano_id, usuario)
    return plano_acao_service.to_detalhe(db, plano)


@router.post("/{plano_id}/verificacao", response_model=PlanoDeAcaoDetalhe)
def registrar_verificacao(
    plano_id: int,
    dados: VerificacaoEficaciaCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_role(*PERFIS_QUALIDADE)),
):
    plano = plano_acao_service.registrar_verificacao(db, plano_id, dados, usuario)
    return plano_acao_service.to_detalhe(db, plano)
