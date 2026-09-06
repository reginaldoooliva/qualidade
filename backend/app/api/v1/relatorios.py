from datetime import date

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.permissions import Perfil
from app.deps import get_current_user, get_db, require_role
from app.schemas.relatorio import ConsolidadoNaoConformidade, ItemConsolidadoPeca
from app.services import relatorio_service

router = APIRouter(prefix="/relatorios", tags=["relatorios"])


@router.get("/pecas/{peca_id}/cpk", dependencies=[Depends(get_current_user)])
def relatorio_cpk_peca(
    peca_id: int,
    data_inicio: date | None = None,
    data_fim: date | None = None,
    operador_id: int | None = None,
    db: Session = Depends(get_db),
):
    pdf = relatorio_service.cpk_pdf_peca(db, peca_id, data_inicio=data_inicio, data_fim=data_fim, operador_id=operador_id)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="cpk_peca_{peca_id}.pdf"'},
    )


@router.get("/pecas/{peca_id}/dados-brutos", dependencies=[Depends(get_current_user)])
def relatorio_dados_brutos(
    peca_id: int,
    etapa_id: int | None = None,
    data_inicio: date | None = None,
    data_fim: date | None = None,
    operador_id: int | None = None,
    db: Session = Depends(get_db),
):
    xlsx = relatorio_service.dados_brutos_xlsx_peca(
        db, peca_id, etapa_id=etapa_id, data_inicio=data_inicio, data_fim=data_fim, operador_id=operador_id
    )
    return Response(
        content=xlsx,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="dados_brutos_peca_{peca_id}.xlsx"'},
    )


@router.get(
    "/pecas/consolidado",
    response_model=list[ItemConsolidadoPeca],
    dependencies=[Depends(require_role(Perfil.GESTOR_QUALIDADE))],
)
def relatorio_consolidado_pecas(db: Session = Depends(get_db)):
    return relatorio_service.consolidado_pecas(db)


@router.get(
    "/pecas/consolidado/pdf",
    dependencies=[Depends(require_role(Perfil.GESTOR_QUALIDADE))],
)
def relatorio_consolidado_pecas_pdf(db: Session = Depends(get_db)):
    pdf = relatorio_service.consolidado_pecas_pdf(db)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="consolidado_pecas.pdf"'},
    )


@router.get(
    "/nao-conformidades/consolidado",
    response_model=ConsolidadoNaoConformidade,
    dependencies=[Depends(require_role(Perfil.GESTOR_QUALIDADE))],
)
def relatorio_consolidado_nc(
    data_inicio: date | None = None,
    data_fim: date | None = None,
    db: Session = Depends(get_db),
):
    return relatorio_service.consolidado_nao_conformidades(db, data_inicio=data_inicio, data_fim=data_fim)


@router.get(
    "/nao-conformidades/consolidado/pdf",
    dependencies=[Depends(require_role(Perfil.GESTOR_QUALIDADE))],
)
def relatorio_consolidado_nc_pdf(
    data_inicio: date | None = None,
    data_fim: date | None = None,
    db: Session = Depends(get_db),
):
    pdf = relatorio_service.consolidado_nao_conformidades_pdf(db, data_inicio=data_inicio, data_fim=data_fim)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="consolidado_nao_conformidades.pdf"'},
    )


@router.get("/nao-conformidades/{nc_id}", dependencies=[Depends(get_current_user)])
def relatorio_rnc(nc_id: int, db: Session = Depends(get_db)):
    pdf = relatorio_service.rnc_pdf(db, nc_id)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="rnc_{nc_id}.pdf"'},
    )
