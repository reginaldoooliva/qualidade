from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.repositories import producao_repository
from app.schemas.coleta import OrdemProducaoRead

router = APIRouter(tags=["ordens"])


@router.get(
    "/pecas/{peca_id}/ordens/{numero_ordem}",
    response_model=OrdemProducaoRead | None,
    dependencies=[Depends(get_current_user)],
)
def obter_ordem(peca_id: int, numero_ordem: str, db: Session = Depends(get_db)):
    return producao_repository.get_by_peca_e_numero(db, peca_id, numero_ordem)
