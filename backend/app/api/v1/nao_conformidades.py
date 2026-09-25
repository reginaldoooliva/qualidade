from datetime import date

from fastapi import APIRouter, Depends, File, Response, UploadFile
from sqlalchemy.orm import Session

from app.core.permissions import PERFIS_QUALIDADE
from app.deps import get_current_user, get_db, require_role
from app.models.nao_conformidade import ClassificacaoNC, OrigemNC, StatusNC
from app.models.usuario import Usuario
from app.schemas.nao_conformidade import (
    AbrirNCRequest,
    AcaoDepartamentalConcluirRequest,
    AcaoDepartamentalCreate,
    AcaoDepartamentalRead,
    IndicadoresNC,
    NaoConformidadeDetalhe,
    NaoConformidadeFotoRead,
    NaoConformidadeListItem,
    TratarNCRequest,
)
from app.services import acao_departamental_service, nao_conformidade_service

router = APIRouter(prefix="/nao-conformidades", tags=["nao-conformidades"])


@router.post("", response_model=NaoConformidadeDetalhe)
def abrir(dados: AbrirNCRequest, db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    nc = nao_conformidade_service.abrir(db, dados, usuario)
    return nao_conformidade_service.to_detalhe(db, nc)


@router.get("", response_model=list[NaoConformidadeListItem], dependencies=[Depends(get_current_user)])
def listar(
    db: Session = Depends(get_db),
    status: StatusNC | None = None,
    peca_id: int | None = None,
    classificacao: ClassificacaoNC | None = None,
    origem: OrigemNC | None = None,
    responsavel_analise_id: int | None = None,
    com_plano: bool | None = None,
    data_inicio: date | None = None,
    data_fim: date | None = None,
):
    ncs = nao_conformidade_service.listar(
        db,
        status=status,
        peca_id=peca_id,
        classificacao=classificacao,
        origem=origem,
        responsavel_analise_id=responsavel_analise_id,
        com_plano=com_plano,
        data_inicio=data_inicio,
        data_fim=data_fim,
    )
    return [nao_conformidade_service.to_list_item(nc) for nc in ncs]


@router.get("/indicadores", response_model=IndicadoresNC, dependencies=[Depends(get_current_user)])
def indicadores(db: Session = Depends(get_db)):
    return nao_conformidade_service.indicadores(db)


@router.get("/{nc_id}", response_model=NaoConformidadeDetalhe, dependencies=[Depends(get_current_user)])
def obter(nc_id: int, db: Session = Depends(get_db)):
    nc = nao_conformidade_service.obter(db, nc_id)
    return nao_conformidade_service.to_detalhe(db, nc)


@router.patch("/{nc_id}/tratamento", response_model=NaoConformidadeDetalhe)
def tratar(
    nc_id: int,
    dados: TratarNCRequest,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_role(*PERFIS_QUALIDADE)),
):
    nc = nao_conformidade_service.tratar(db, nc_id, dados, usuario)
    return nao_conformidade_service.to_detalhe(db, nc)


@router.post("/{nc_id}/encerrar", response_model=NaoConformidadeDetalhe)
def encerrar(
    nc_id: int,
    ignorar_pendencias: bool = False,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_role(*PERFIS_QUALIDADE)),
):
    nc = nao_conformidade_service.encerrar(db, nc_id, usuario, ignorar_pendencias=ignorar_pendencias)
    return nao_conformidade_service.to_detalhe(db, nc)


@router.post("/{nc_id}/acoes-departamentais", response_model=AcaoDepartamentalRead, status_code=201)
def adicionar_acao_departamental(
    nc_id: int,
    dados: AcaoDepartamentalCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_role(*PERFIS_QUALIDADE)),
):
    return acao_departamental_service.adicionar(db, nc_id, dados, usuario)


@router.delete("/{nc_id}/acoes-departamentais/{acao_id}", status_code=204)
def remover_acao_departamental(
    nc_id: int,
    acao_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_role(*PERFIS_QUALIDADE)),
):
    acao_departamental_service.remover(db, nc_id, acao_id, usuario)


@router.patch("/{nc_id}/acoes-departamentais/{acao_id}/concluir", response_model=AcaoDepartamentalRead)
def concluir_acao_departamental(
    nc_id: int,
    acao_id: int,
    dados: AcaoDepartamentalConcluirRequest,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return acao_departamental_service.concluir(db, nc_id, acao_id, dados, usuario)


@router.post("/{nc_id}/fotos", response_model=list[NaoConformidadeFotoRead], status_code=201)
async def anexar_fotos(
    nc_id: int,
    arquivos: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    fotos = []
    for arquivo in arquivos:
        conteudo = await arquivo.read()
        foto = nao_conformidade_service.anexar_foto(
            db, nc_id, arquivo.filename or "foto", arquivo.content_type or "", conteudo, usuario
        )
        fotos.append(foto)
    return fotos


@router.get("/{nc_id}/fotos/{foto_id}", dependencies=[Depends(get_current_user)])
def obter_foto(nc_id: int, foto_id: int, db: Session = Depends(get_db)):
    foto = nao_conformidade_service.obter_foto(db, nc_id, foto_id)
    return Response(content=foto.conteudo, media_type=foto.content_type)


@router.delete(
    "/{nc_id}/fotos/{foto_id}", status_code=204, dependencies=[Depends(require_role(*PERFIS_QUALIDADE))]
)
def remover_foto(nc_id: int, foto_id: int, db: Session = Depends(get_db)):
    nao_conformidade_service.remover_foto(db, nc_id, foto_id)
