from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.permissions import PERFIS_QUALIDADE
from app.deps import get_current_user, get_db, require_role
from app.schemas.caracteristica import CaracteristicaCreate, CaracteristicaRead, CaracteristicaUpdate
from app.services import caracteristica_service

router = APIRouter(tags=["caracteristicas"])


@router.get(
    "/etapas/{etapa_id}/caracteristicas",
    response_model=list[CaracteristicaRead],
    dependencies=[Depends(get_current_user)],
)
def listar(etapa_id: int, db: Session = Depends(get_db)):
    return caracteristica_service.listar_por_etapa(db, etapa_id)


@router.get(
    "/caracteristicas/{caracteristica_id}",
    response_model=CaracteristicaRead,
    dependencies=[Depends(get_current_user)],
)
def obter(caracteristica_id: int, db: Session = Depends(get_db)):
    return caracteristica_service.obter(db, caracteristica_id)


@router.post(
    "/etapas/{etapa_id}/caracteristicas",
    response_model=CaracteristicaRead,
    status_code=201,
    dependencies=[Depends(require_role(*PERFIS_QUALIDADE))],
)
def criar(etapa_id: int, dados: CaracteristicaCreate, db: Session = Depends(get_db)):
    return caracteristica_service.criar(db, etapa_id, dados)


@router.put(
    "/caracteristicas/{caracteristica_id}",
    response_model=CaracteristicaRead,
    dependencies=[Depends(require_role(*PERFIS_QUALIDADE))],
)
def atualizar(caracteristica_id: int, dados: CaracteristicaUpdate, db: Session = Depends(get_db)):
    return caracteristica_service.atualizar(db, caracteristica_id, dados)


@router.patch(
    "/caracteristicas/{caracteristica_id}/inativar",
    response_model=CaracteristicaRead,
    dependencies=[Depends(require_role(*PERFIS_QUALIDADE))],
)
def inativar(caracteristica_id: int, db: Session = Depends(get_db)):
    return caracteristica_service.inativar(db, caracteristica_id)
