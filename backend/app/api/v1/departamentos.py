from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.permissions import PERFIS_QUALIDADE
from app.deps import get_current_user, get_db, require_role
from app.schemas.departamento import DepartamentoCreate, DepartamentoRead, DepartamentoUpdate
from app.services import departamento_service

router = APIRouter(prefix="/departamentos", tags=["departamentos"])


@router.get("", response_model=list[DepartamentoRead], dependencies=[Depends(get_current_user)])
def listar(busca: str | None = None, db: Session = Depends(get_db)):
    return departamento_service.listar(db, busca=busca)


@router.get("/{departamento_id}", response_model=DepartamentoRead, dependencies=[Depends(get_current_user)])
def obter(departamento_id: int, db: Session = Depends(get_db)):
    return departamento_service.obter(db, departamento_id)


@router.post(
    "", response_model=DepartamentoRead, status_code=201, dependencies=[Depends(require_role(*PERFIS_QUALIDADE))]
)
def criar(dados: DepartamentoCreate, db: Session = Depends(get_db)):
    return departamento_service.criar(db, dados)


@router.put(
    "/{departamento_id}", response_model=DepartamentoRead, dependencies=[Depends(require_role(*PERFIS_QUALIDADE))]
)
def atualizar(departamento_id: int, dados: DepartamentoUpdate, db: Session = Depends(get_db)):
    return departamento_service.atualizar(db, departamento_id, dados)


@router.patch(
    "/{departamento_id}/inativar",
    response_model=DepartamentoRead,
    dependencies=[Depends(require_role(*PERFIS_QUALIDADE))],
)
def inativar(departamento_id: int, db: Session = Depends(get_db)):
    return departamento_service.inativar(db, departamento_id)


@router.patch(
    "/{departamento_id}/ativar",
    response_model=DepartamentoRead,
    dependencies=[Depends(require_role(*PERFIS_QUALIDADE))],
)
def ativar(departamento_id: int, db: Session = Depends(get_db)):
    return departamento_service.ativar(db, departamento_id)
