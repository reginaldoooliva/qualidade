from fastapi import APIRouter, Depends, File, Response, UploadFile
from sqlalchemy.orm import Session

from app.core.exceptions import RecursoNaoEncontradoError
from app.core.permissions import PERFIS_QUALIDADE
from app.deps import get_current_user, get_db, require_role
from app.models.peca import StatusCadastro
from app.schemas.tipo_instrumento import TipoInstrumentoCreate, TipoInstrumentoRead, TipoInstrumentoUpdate
from app.services import tipo_instrumento_service

router = APIRouter(prefix="/tipos-instrumento", tags=["tipos-instrumento"])


@router.get("", response_model=list[TipoInstrumentoRead], dependencies=[Depends(get_current_user)])
def listar(busca: str | None = None, status: StatusCadastro | None = None, db: Session = Depends(get_db)):
    return tipo_instrumento_service.listar(db, busca=busca, status=status)


@router.get("/{tipo_id}", response_model=TipoInstrumentoRead, dependencies=[Depends(get_current_user)])
def obter(tipo_id: int, db: Session = Depends(get_db)):
    return tipo_instrumento_service.obter(db, tipo_id)


@router.post(
    "", response_model=TipoInstrumentoRead, status_code=201, dependencies=[Depends(require_role(*PERFIS_QUALIDADE))]
)
def criar(dados: TipoInstrumentoCreate, db: Session = Depends(get_db)):
    return tipo_instrumento_service.criar(db, dados)


@router.put(
    "/{tipo_id}", response_model=TipoInstrumentoRead, dependencies=[Depends(require_role(*PERFIS_QUALIDADE))]
)
def atualizar(tipo_id: int, dados: TipoInstrumentoUpdate, db: Session = Depends(get_db)):
    return tipo_instrumento_service.atualizar(db, tipo_id, dados)


@router.patch(
    "/{tipo_id}/inativar",
    response_model=TipoInstrumentoRead,
    dependencies=[Depends(require_role(*PERFIS_QUALIDADE))],
)
def inativar(tipo_id: int, db: Session = Depends(get_db)):
    return tipo_instrumento_service.inativar(db, tipo_id)


@router.patch(
    "/{tipo_id}/ativar", response_model=TipoInstrumentoRead, dependencies=[Depends(require_role(*PERFIS_QUALIDADE))]
)
def ativar(tipo_id: int, db: Session = Depends(get_db)):
    return tipo_instrumento_service.ativar(db, tipo_id)


@router.post(
    "/{tipo_id}/imagem",
    response_model=TipoInstrumentoRead,
    dependencies=[Depends(require_role(*PERFIS_QUALIDADE))],
)
async def anexar_imagem(tipo_id: int, arquivo: UploadFile = File(...), db: Session = Depends(get_db)):
    conteudo = await arquivo.read()
    return tipo_instrumento_service.anexar_imagem(
        db, tipo_id, arquivo.filename or "imagem", arquivo.content_type or "", conteudo
    )


@router.get("/{tipo_id}/imagem", dependencies=[Depends(get_current_user)])
def obter_imagem(tipo_id: int, db: Session = Depends(get_db)):
    tipo = tipo_instrumento_service.obter(db, tipo_id)
    if not tipo.imagem_conteudo:
        raise RecursoNaoEncontradoError("Este tipo de instrumento não tem imagem anexada")
    return Response(content=tipo.imagem_conteudo, media_type=tipo.imagem_content_type)
