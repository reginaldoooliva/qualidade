from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.permissions import PERFIS_QUALIDADE
from app.deps import get_current_user, get_db, require_role
from app.models.nao_conformidade import ClassificacaoNC, OrigemNC, StatusNC
from app.models.usuario import Usuario
from app.schemas.nao_conformidade import (
    AbrirNCRequest,
    IndicadoresNC,
    NaoConformidadeDetalhe,
    NaoConformidadeListItem,
    TratarNCRequest,
)
from app.services import nao_conformidade_service

router = APIRouter(prefix="/nao-conformidades", tags=["nao-conformidades"])


@router.post("", response_model=NaoConformidadeDetalhe)
def abrir(dados: AbrirNCRequest, db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    nc = nao_conformidade_service.abrir(db, dados, usuario)
    return nao_conformidade_service.to_detalhe(db, nc)


@router.get("", response_model=list[NaoConformidadeListItem], dependencies=[Depends(get_current_user)])
def listar(
    db: Session = Depends(get_db),
    status: StatusNC | None = None,
    peca_id: int | None = None,
    classificacao: ClassificacaoNC | None = None,
    origem: OrigemNC | None = None,
    responsavel_analise_id: int | None = None,
    com_plano: bool | None = None,
    data_inicio: date | None = None,
    data_fim: date | None = None,
):
    ncs = nao_conformidade_service.listar(
        db,
        status=status,
        peca_id=peca_id,
        classificacao=classificacao,
        origem=origem,
        responsavel_analise_id=responsavel_analise_id,
        com_plano=com_plano,
        data_inicio=data_inicio,
        data_fim=data_fim,
    )
    return [nao_conformidade_service.to_list_item(nc) for nc in ncs]


@router.get("/indicadores", response_model=IndicadoresNC, dependencies=[Depends(get_current_user)])
def indicadores(db: Session = Depends(get_db)):
    return nao_conformidade_service.indicadores(db)


@router.get("/{nc_id}", response_model=NaoConformidadeDetalhe, dependencies=[Depends(get_current_user)])
def obter(nc_id: int, db: Session = Depends(get_db)):
    nc = nao_conformidade_service.obter(db, nc_id)
    return nao_conformidade_service.to_detalhe(db, nc)


@router.patch("/{nc_id}/tratamento", response_model=NaoConformidadeDetalhe)
def tratar(
    nc_id: int,
    dados: TratarNCRequest,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_role(*PERFIS_QUALIDADE)),
):
    nc = nao_conformidade_service.tratar(db, nc_id, dados, usuario)
    return nao_conformidade_service.to_detalhe(db, nc)


@router.post("/{nc_id}/encerrar", response_model=NaoConformidadeDetalhe)
def encerrar(
    nc_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_role(*PERFIS_QUALIDADE)),
):
    nc = nao_conformidade_service.encerrar(db, nc_id, usuario)
    return nao_conformidade_service.to_detalhe(db, nc)
