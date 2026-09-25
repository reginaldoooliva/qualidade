from fastapi import APIRouter, Depends, File, Response, UploadFile
from sqlalchemy.orm import Session

from app.core.exceptions import RecursoNaoEncontradoError
from app.core.permissions import PERFIS_QUALIDADE
from app.deps import get_current_user, get_db, require_role
from app.models.bloqueio_deposito import StatusBloqueioDeposito
from app.models.usuario import Usuario
from app.schemas.bloqueio_deposito import (
    BloqueioDepositoCreate,
    BloqueioDepositoLiberar,
    BloqueioDepositoRead,
    PecaComBloqueiosRead,
)
from app.services import bloqueio_deposito_service

router = APIRouter(prefix="/deposito-qualidade", tags=["deposito-qualidade"])


@router.get("/buscar", response_model=PecaComBloqueiosRead, dependencies=[Depends(get_current_user)])
def buscar_por_codigo_peca(codigo_peca: str, db: Session = Depends(get_db)):
    peca, bloqueios = bloqueio_deposito_service.buscar_por_codigo_peca(db, codigo_peca)
    return PecaComBloqueiosRead(peca=peca, bloqueios=bloqueios)


@router.get("", response_model=list[BloqueioDepositoRead], dependencies=[Depends(get_current_user)])
def listar(status: StatusBloqueioDeposito | None = None, busca: str | None = None, db: Session = Depends(get_db)):
    return bloqueio_deposito_service.listar(db, status=status, busca=busca)


@router.get("/{bloqueio_id}", response_model=BloqueioDepositoRead, dependencies=[Depends(get_current_user)])
def obter(bloqueio_id: int, db: Session = Depends(get_db)):
    return bloqueio_deposito_service.obter(db, bloqueio_id)


@router.post(
    "", response_model=BloqueioDepositoRead, status_code=201, dependencies=[Depends(require_role(*PERFIS_QUALIDADE))]
)
def criar(
    dados: BloqueioDepositoCreate, db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)
):
    return bloqueio_deposito_service.criar(db, dados, usuario)


@router.patch(
    "/{bloqueio_id}/liberar",
    response_model=BloqueioDepositoRead,
    dependencies=[Depends(require_role(*PERFIS_QUALIDADE))],
)
def liberar(
    bloqueio_id: int,
    dados: BloqueioDepositoLiberar,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return bloqueio_deposito_service.liberar(db, bloqueio_id, dados, usuario)


@router.post(
    "/{bloqueio_id}/foto",
    response_model=BloqueioDepositoRead,
    dependencies=[Depends(require_role(*PERFIS_QUALIDADE))],
)
async def anexar_foto(
    bloqueio_id: int,
    arquivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    conteudo = await arquivo.read()
    return bloqueio_deposito_service.anexar_foto(
        db, bloqueio_id, arquivo.filename or "foto", arquivo.content_type or "", conteudo, usuario
    )


@router.get("/{bloqueio_id}/foto", dependencies=[Depends(get_current_user)])
def obter_foto(bloqueio_id: int, db: Session = Depends(get_db)):
    bloqueio = bloqueio_deposito_service.obter(db, bloqueio_id)
    if not bloqueio.foto_conteudo:
        raise RecursoNaoEncontradoError("Este bloqueio não tem foto anexada")
    return Response(content=bloqueio.foto_conteudo, media_type=bloqueio.foto_content_type)
