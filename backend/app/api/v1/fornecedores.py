from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.permissions import PERFIS_QUALIDADE
from app.deps import get_current_user, get_db, require_role
from app.schemas.fornecedor import FornecedorCreate, FornecedorRead, FornecedorUpdate
from app.services import fornecedor_service

router = APIRouter(prefix="/fornecedores", tags=["fornecedores"])


@router.get("", response_model=list[FornecedorRead], dependencies=[Depends(get_current_user)])
def listar(busca: str | None = None, db: Session = Depends(get_db)):
    return fornecedor_service.listar(db, busca=busca)


@router.get("/{fornecedor_id}", response_model=FornecedorRead, dependencies=[Depends(get_current_user)])
def obter(fornecedor_id: int, db: Session = Depends(get_db)):
    return fornecedor_service.obter(db, fornecedor_id)


@router.post(
    "", response_model=FornecedorRead, status_code=201, dependencies=[Depends(require_role(*PERFIS_QUALIDADE))]
)
def criar(dados: FornecedorCreate, db: Session = Depends(get_db)):
    return fornecedor_service.criar(db, dados)


@router.put(
    "/{fornecedor_id}", response_model=FornecedorRead, dependencies=[Depends(require_role(*PERFIS_QUALIDADE))]
)
def atualizar(fornecedor_id: int, dados: FornecedorUpdate, db: Session = Depends(get_db)):
    return fornecedor_service.atualizar(db, fornecedor_id, dados)


@router.patch(
    "/{fornecedor_id}/inativar",
    response_model=FornecedorRead,
    dependencies=[Depends(require_role(*PERFIS_QUALIDADE))],
)
def inativar(fornecedor_id: int, db: Session = Depends(get_db)):
    return fornecedor_service.inativar(db, fornecedor_id)


@router.patch(
    "/{fornecedor_id}/ativar", response_model=FornecedorRead, dependencies=[Depends(require_role(*PERFIS_QUALIDADE))]
)
def ativar(fornecedor_id: int, db: Session = Depends(get_db)):
    return fornecedor_service.ativar(db, fornecedor_id)
