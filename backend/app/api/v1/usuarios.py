from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.repositories import usuario_repository
from app.schemas.usuario import UsuarioRead

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.get("", response_model=list[UsuarioRead], dependencies=[Depends(get_current_user)])
def listar(db: Session = Depends(get_db)):
    return usuario_repository.list_ativos(db)
