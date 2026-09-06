from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.permissions import PERFIS_QUALIDADE
from app.deps import get_current_user, get_db, require_role
from app.schemas.etapa import EtapaCreate, EtapaRead, EtapaUpdate
from app.services import etapa_service

router = APIRouter(tags=["etapas"])


@router.get("/pecas/{peca_id}/etapas", response_model=list[EtapaRead], dependencies=[Depends(get_current_user)])
def listar(peca_id: int, db: Session = Depends(get_db)):
    return etapa_service.listar_por_peca(db, peca_id)


@router.get("/etapas/{etapa_id}", response_model=EtapaRead, dependencies=[Depends(get_current_user)])
def obter(etapa_id: int, db: Session = Depends(get_db)):
    return etapa_service.obter(db, etapa_id)


@router.post(
    "/pecas/{peca_id}/etapas",
    response_model=EtapaRead,
    status_code=201,
    dependencies=[Depends(require_role(*PERFIS_QUALIDADE))],
)
def criar(peca_id: int, dados: EtapaCreate, db: Session = Depends(get_db)):
    return etapa_service.criar(db, peca_id, dados)


@router.put("/etapas/{etapa_id}", response_model=EtapaRead, dependencies=[Depends(require_role(*PERFIS_QUALIDADE))])
def atualizar(etapa_id: int, dados: EtapaUpdate, db: Session = Depends(get_db)):
    return etapa_service.atualizar(db, etapa_id, dados)


@router.patch(
    "/etapas/{etapa_id}/inativar",
    response_model=EtapaRead,
    dependencies=[Depends(require_role(*PERFIS_QUALIDADE))],
)
def inativar(etapa_id: int, db: Session = Depends(get_db)):
    return etapa_service.inativar(db, etapa_id)
