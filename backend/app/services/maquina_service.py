from sqlalchemy.orm import Session

from app.core.exceptions import RecursoNaoEncontradoError, RegraNegocioError
from app.models.maquina import Maquina
from app.models.peca import StatusCadastro
from app.repositories import maquina_repository
from app.schemas.maquina import MaquinaCreate, MaquinaUpdate


def listar(db: Session, busca: str | None = None) -> list[Maquina]:
    return maquina_repository.list_maquinas(db, busca=busca)


def obter(db: Session, maquina_id: int) -> Maquina:
    maquina = maquina_repository.get_by_id(db, maquina_id)
    if not maquina:
        raise RecursoNaoEncontradoError(f"Máquina {maquina_id} não encontrada")
    return maquina


def criar(db: Session, dados: MaquinaCreate) -> Maquina:
    if maquina_repository.get_by_codigo(db, dados.codigo):
        raise RegraNegocioError(f"Já existe uma máquina com o código '{dados.codigo}'", code="CODIGO_DUPLICADO")
    maquina = Maquina(**dados.model_dump())
    return maquina_repository.create(db, maquina)


def atualizar(db: Session, maquina_id: int, dados: MaquinaUpdate) -> Maquina:
    maquina = obter(db, maquina_id)
    novos_dados = dados.model_dump(exclude_unset=True)

    novo_codigo = novos_dados.get("codigo")
    if novo_codigo and novo_codigo != maquina.codigo:
        existente = maquina_repository.get_by_codigo(db, novo_codigo)
        if existente and existente.id != maquina.id:
            raise RegraNegocioError(
                f"Já existe uma máquina com o código '{novo_codigo}'", code="CODIGO_DUPLICADO"
            )

    for campo, valor in novos_dados.items():
        setattr(maquina, campo, valor)
    return maquina_repository.update(db, maquina)


def inativar(db: Session, maquina_id: int) -> Maquina:
    maquina = obter(db, maquina_id)
    maquina.status = StatusCadastro.INATIVO
    return maquina_repository.update(db, maquina)


def ativar(db: Session, maquina_id: int) -> Maquina:
    maquina = obter(db, maquina_id)
    maquina.status = StatusCadastro.ATIVO
    return maquina_repository.update(db, maquina)
