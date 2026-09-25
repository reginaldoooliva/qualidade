from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.exceptions import RecursoNaoEncontradoError
from app.core.permissions import PERFIS_GESTAO
from app.deps import get_current_user, get_db, require_role
from app.repositories import usuario_repository
from app.services import departamento_service
from app.schemas.usuario import AtualizarDepartamentoRequest, UsuarioRead

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.get("", response_model=list[UsuarioRead], dependencies=[Depends(get_current_user)])
def listar(db: Session = Depends(get_db)):
    return usuario_repository.list_ativos(db)


@router.patch(
    "/{usuario_id}/departamento",
    response_model=UsuarioRead,
    dependencies=[Depends(require_role(*PERFIS_GESTAO))],
)
def atualizar_departamento(usuario_id: int, dados: AtualizarDepartamentoRequest, db: Session = Depends(get_db)):
    usuario = usuario_repository.get_by_id(db, usuario_id)
    if not usuario:
        raise RecursoNaoEncontradoError(f"Usuário {usuario_id} não encontrado")
    if dados.departamento_id is not None:
        departamento_service.obter(db, dados.departamento_id)
    usuario.departamento_id = dados.departamento_id
    return usuario_repository.update(db, usuario)
