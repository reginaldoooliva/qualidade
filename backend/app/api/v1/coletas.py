from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.permissions import PERFIS_QUALIDADE
from app.deps import get_current_user, get_db, require_role
from app.models.usuario import Usuario
from app.schemas.coleta import (
    FinalizarColetaRequest,
    FinalizarColetaResponse,
    IniciarColetaRequest,
    MedicaoRead,
    MedicaoUpsert,
    RodadaColetaDetalhe,
)
from app.services import coleta_service

router = APIRouter(prefix="/coletas", tags=["coletas"])


@router.post("/iniciar", response_model=RodadaColetaDetalhe, dependencies=[Depends(get_current_user)])
def iniciar(dados: IniciarColetaRequest, db: Session = Depends(get_db)):
    return coleta_service.iniciar(db, dados)


@router.get("/{rodada_id}", response_model=RodadaColetaDetalhe, dependencies=[Depends(get_current_user)])
def obter(rodada_id: int, db: Session = Depends(get_db)):
    return coleta_service.obter(db, rodada_id)


@router.put("/{rodada_id}/medicoes/{caracteristica_id}/{amostra_numero}", response_model=MedicaoRead)
def salvar_medicao(
    rodada_id: int,
    caracteristica_id: int,
    amostra_numero: int,
    dados: MedicaoUpsert,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return coleta_service.salvar_medicao(db, rodada_id, caracteristica_id, amostra_numero, dados.valor, usuario)


@router.delete("/{rodada_id}/medicoes/{caracteristica_id}/{amostra_numero}", status_code=204)
def excluir_medicao(
    rodada_id: int,
    caracteristica_id: int,
    amostra_numero: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    coleta_service.excluir_medicao(db, rodada_id, caracteristica_id, amostra_numero)


@router.post("/{rodada_id}/finalizar", response_model=FinalizarColetaResponse)
def finalizar(
    rodada_id: int,
    dados: FinalizarColetaRequest,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    rodada, sugestao = coleta_service.finalizar(db, rodada_id, dados)
    resposta = FinalizarColetaResponse.model_validate(rodada)
    resposta.sugestao_abrir_rnc = sugestao
    return resposta


@router.post("/{rodada_id}/reabrir", response_model=RodadaColetaDetalhe)
def reabrir(
    rodada_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_role(*PERFIS_QUALIDADE)),
):
    return coleta_service.reabrir(db, rodada_id, usuario)
