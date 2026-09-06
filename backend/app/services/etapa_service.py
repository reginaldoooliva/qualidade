from sqlalchemy.orm import Session

from app.core.exceptions import RecursoNaoEncontradoError, RegraNegocioError
from app.models.peca import Etapa, StatusCadastro
from app.repositories import etapa_repository
from app.services import peca_service
from app.schemas.etapa import EtapaCreate, EtapaUpdate


def listar_por_peca(db: Session, peca_id: int) -> list[Etapa]:
    peca_service.obter(db, peca_id)  # garante que a peça existe
    return etapa_repository.list_by_peca(db, peca_id)


def obter(db: Session, etapa_id: int) -> Etapa:
    etapa = etapa_repository.get_by_id(db, etapa_id)
    if not etapa:
        raise RecursoNaoEncontradoError(f"Etapa {etapa_id} não encontrada")
    return etapa


def criar(db: Session, peca_id: int, dados: EtapaCreate) -> Etapa:
    peca_service.obter(db, peca_id)
    if etapa_repository.get_by_peca_e_numero(db, peca_id, dados.numero_etapa):
        raise RegraNegocioError(
            f"A peça já possui uma etapa com número {dados.numero_etapa}", code="ETAPA_NUMERO_DUPLICADO"
        )
    etapa = Etapa(peca_id=peca_id, **dados.model_dump())
    return etapa_repository.create(db, etapa)


def atualizar(db: Session, etapa_id: int, dados: EtapaUpdate) -> Etapa:
    etapa = obter(db, etapa_id)
    novos_dados = dados.model_dump(exclude_unset=True)

    novo_numero = novos_dados.get("numero_etapa")
    if novo_numero is not None and novo_numero != etapa.numero_etapa:
        existente = etapa_repository.get_by_peca_e_numero(db, etapa.peca_id, novo_numero)
        if existente and existente.id != etapa.id:
            raise RegraNegocioError(
                f"A peça já possui uma etapa com número {novo_numero}", code="ETAPA_NUMERO_DUPLICADO"
            )

    for campo, valor in novos_dados.items():
        setattr(etapa, campo, valor)
    return etapa_repository.update(db, etapa)


def inativar(db: Session, etapa_id: int) -> Etapa:
    etapa = obter(db, etapa_id)
    etapa.status = StatusCadastro.INATIVO
    return etapa_repository.update(db, etapa)
