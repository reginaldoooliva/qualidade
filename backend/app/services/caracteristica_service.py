from sqlalchemy.orm import Session

from app.core.exceptions import RecursoNaoEncontradoError, RegraNegocioError
from app.models.peca import Caracteristica, StatusCadastro
from app.repositories import caracteristica_repository
from app.services import etapa_service
from app.schemas.caracteristica import CaracteristicaCreate, CaracteristicaUpdate


def _validar_tolerancias(nominal: float, tol_superior: float, tol_inferior: float) -> None:
    if tol_superior == 0 and tol_inferior == 0:
        raise RegraNegocioError(
            "Informe ao menos uma tolerância (superior ou inferior)", code="TOLERANCIA_AUSENTE"
        )
    lse = nominal + tol_superior
    lie = nominal - tol_inferior
    if lse <= lie:
        raise RegraNegocioError("O limite superior (LSE) deve ser maior que o limite inferior (LIE)", code="LSE_MENOR_LIE")


def listar_por_etapa(db: Session, etapa_id: int) -> list[Caracteristica]:
    etapa_service.obter(db, etapa_id)
    return caracteristica_repository.list_by_etapa(db, etapa_id)


def obter(db: Session, caracteristica_id: int) -> Caracteristica:
    caracteristica = caracteristica_repository.get_by_id(db, caracteristica_id)
    if not caracteristica:
        raise RecursoNaoEncontradoError(f"Característica {caracteristica_id} não encontrada")
    return caracteristica


def criar(db: Session, etapa_id: int, dados: CaracteristicaCreate) -> Caracteristica:
    etapa_service.obter(db, etapa_id)
    _validar_tolerancias(dados.nominal, dados.tol_superior, dados.tol_inferior)
    caracteristica = Caracteristica(etapa_id=etapa_id, **dados.model_dump())
    return caracteristica_repository.create(db, caracteristica)


def atualizar(db: Session, caracteristica_id: int, dados: CaracteristicaUpdate) -> Caracteristica:
    caracteristica = obter(db, caracteristica_id)
    novos_dados = dados.model_dump(exclude_unset=True)

    nominal = novos_dados.get("nominal", float(caracteristica.nominal))
    tol_superior = novos_dados.get("tol_superior", float(caracteristica.tol_superior))
    tol_inferior = novos_dados.get("tol_inferior", float(caracteristica.tol_inferior))
    if {"nominal", "tol_superior", "tol_inferior"} & novos_dados.keys():
        _validar_tolerancias(nominal, tol_superior, tol_inferior)

    for campo, valor in novos_dados.items():
        setattr(caracteristica, campo, valor)
    return caracteristica_repository.update(db, caracteristica)


def inativar(db: Session, caracteristica_id: int) -> Caracteristica:
    caracteristica = obter(db, caracteristica_id)
    caracteristica.status = StatusCadastro.INATIVO
    return caracteristica_repository.update(db, caracteristica)
