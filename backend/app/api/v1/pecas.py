from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.permissions import PERFIS_QUALIDADE
from app.deps import get_current_user, get_db, require_role
from app.schemas.peca import PecaCreate, PecaListItem, PecaRead, PecaUpdate
from app.services import peca_service

router = APIRouter(prefix="/pecas", tags=["pecas"])


@router.get("", response_model=list[PecaListItem], dependencies=[Depends(get_current_user)])
def listar(busca: str | None = None, cliente: str | None = None, db: Session = Depends(get_db)):
    return peca_service.listar(db, busca=busca, cliente=cliente)


@router.get("/{peca_id}", response_model=PecaRead, dependencies=[Depends(get_current_user)])
def obter(peca_id: int, db: Session = Depends(get_db)):
    return peca_service.obter(db, peca_id)


@router.post("", response_model=PecaRead, status_code=201, dependencies=[Depends(require_role(*PERFIS_QUALIDADE))])
def criar(dados: PecaCreate, db: Session = Depends(get_db)):
    return peca_service.criar(db, dados)


@router.put("/{peca_id}", response_model=PecaRead, dependencies=[Depends(require_role(*PERFIS_QUALIDADE))])
def atualizar(peca_id: int, dados: PecaUpdate, db: Session = Depends(get_db)):
    return peca_service.atualizar(db, peca_id, dados)


@router.patch("/{peca_id}/inativar", response_model=PecaRead, dependencies=[Depends(require_role(*PERFIS_QUALIDADE))])
def inativar(peca_id: int, db: Session = Depends(get_db)):
    return peca_service.inativar(db, peca_id)


@router.patch("/{peca_id}/ativar", response_model=PecaRead, dependencies=[Depends(require_role(*PERFIS_QUALIDADE))])
def ativar(peca_id: int, db: Session = Depends(get_db)):
    return peca_service.ativar(db, peca_id)
