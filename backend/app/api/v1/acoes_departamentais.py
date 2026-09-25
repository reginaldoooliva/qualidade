from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.permissions import PERFIS_QUALIDADE
from app.deps import get_current_user, get_db
from app.models.usuario import Usuario
from app.schemas.nao_conformidade import AcaoDepartamentalListItem
from app.services import acao_departamental_service

router = APIRouter(prefix="/acoes-departamentais", tags=["acoes-departamentais"])


@router.get("", response_model=list[AcaoDepartamentalListItem])
def listar_pendentes(
    departamento_id: int | None = None,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    if usuario.perfil not in PERFIS_QUALIDADE:
        departamento_id = usuario.departamento_id
        if departamento_id is None:
            return []
    acoes = acao_departamental_service.listar_pendentes(db, departamento_id=departamento_id)
    itens = []
    for acao in acoes:
        item = AcaoDepartamentalListItem.model_validate(acao)
        item.numero_rnc = acao.nao_conformidade.numero_rnc
        item.peca_codigo = acao.nao_conformidade.peca.codigo
        item.peca_descricao = acao.nao_conformidade.peca.descricao
        itens.append(item)
    return itens
