from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.repositories import analise_repository
from app.schemas.analise import AnaliseCapabilidadeResponse, RodadaResumo
from app.schemas.carta_controle import CartaControleResponse
from app.services import capabilidade_service, carta_controle_service

router = APIRouter(tags=["analise"])


@router.get(
    "/pecas/{peca_id}/etapas/{etapa_id}/rodadas",
    response_model=list[RodadaResumo],
    dependencies=[Depends(get_current_user)],
)
def listar_rodadas(peca_id: int, etapa_id: int, db: Session = Depends(get_db)):
    return analise_repository.list_rodadas_para_analise(db, peca_id, etapa_id)


@router.get(
    "/analise/pecas/{peca_id}/etapas/{etapa_id}/capabilidade",
    response_model=AnaliseCapabilidadeResponse,
    dependencies=[Depends(get_current_user)],
)
def analisar_capabilidade(
    peca_id: int,
    etapa_id: int,
    rodada_id: int | None = None,
    data_inicio: date | None = None,
    data_fim: date | None = None,
    operador_id: int | None = None,
    db: Session = Depends(get_db),
):
    return capabilidade_service.analisar(
        db,
        peca_id,
        etapa_id,
        rodada_id=rodada_id,
        data_inicio=data_inicio,
        data_fim=data_fim,
        operador_id=operador_id,
    )


@router.get(
    "/analise/pecas/{peca_id}/etapas/{etapa_id}/carta-controle",
    response_model=CartaControleResponse,
    dependencies=[Depends(get_current_user)],
)
def carta_controle(
    peca_id: int,
    etapa_id: int,
    rodada_id: int | None = None,
    data_inicio: date | None = None,
    data_fim: date | None = None,
    operador_id: int | None = None,
    db: Session = Depends(get_db),
):
    return carta_controle_service.calcular(
        db,
        peca_id,
        etapa_id,
        rodada_id=rodada_id,
        data_inicio=data_inicio,
        data_fim=data_fim,
        operador_id=operador_id,
    )
