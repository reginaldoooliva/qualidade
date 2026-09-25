from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.permissions import PERFIS_QUALIDADE
from app.deps import get_current_user, get_db, require_role
from app.schemas.maquina import MaquinaCreate, MaquinaRead, MaquinaUpdate
from app.services import maquina_service

router = APIRouter(prefix="/maquinas", tags=["maquinas"])


@router.get("", response_model=list[MaquinaRead], dependencies=[Depends(get_current_user)])
def listar(busca: str | None = None, db: Session = Depends(get_db)):
    return maquina_service.listar(db, busca=busca)


@router.get("/{maquina_id}", response_model=MaquinaRead, dependencies=[Depends(get_current_user)])
def obter(maquina_id: int, db: Session = Depends(get_db)):
    return maquina_service.obter(db, maquina_id)


@router.post("", response_model=MaquinaRead, status_code=201, dependencies=[Depends(require_role(*PERFIS_QUALIDADE))])
def criar(dados: MaquinaCreate, db: Session = Depends(get_db)):
    return maquina_service.criar(db, dados)


@router.put("/{maquina_id}", response_model=MaquinaRead, dependencies=[Depends(require_role(*PERFIS_QUALIDADE))])
def atualizar(maquina_id: int, dados: MaquinaUpdate, db: Session = Depends(get_db)):
    return maquina_service.atualizar(db, maquina_id, dados)


@router.patch(
    "/{maquina_id}/inativar", response_model=MaquinaRead, dependencies=[Depends(require_role(*PERFIS_QUALIDADE))]
)
def inativar(maquina_id: int, db: Session = Depends(get_db)):
    return maquina_service.inativar(db, maquina_id)


@router.patch(
    "/{maquina_id}/ativar", response_model=MaquinaRead, dependencies=[Depends(require_role(*PERFIS_QUALIDADE))]
)
def ativar(maquina_id: int, db: Session = Depends(get_db)):
    return maquina_service.ativar(db, maquina_id)
