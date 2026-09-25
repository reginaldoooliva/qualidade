from sqlalchemy.orm import Session

from app.core.exceptions import RecursoNaoEncontradoError, RegraNegocioError
from app.models.departamento import Departamento
from app.models.peca import StatusCadastro
from app.repositories import departamento_repository
from app.schemas.departamento import DepartamentoCreate, DepartamentoUpdate


def listar(db: Session, busca: str | None = None) -> list[Departamento]:
    return departamento_repository.list_departamentos(db, busca=busca)


def obter(db: Session, departamento_id: int) -> Departamento:
    departamento = departamento_repository.get_by_id(db, departamento_id)
    if not departamento:
        raise RecursoNaoEncontradoError(f"Departamento {departamento_id} não encontrado")
    return departamento


def criar(db: Session, dados: DepartamentoCreate) -> Departamento:
    if departamento_repository.get_by_nome(db, dados.nome):
        raise RegraNegocioError(
            f"Já existe um departamento com o nome '{dados.nome}'", code="NOME_DUPLICADO"
        )
    departamento = Departamento(**dados.model_dump())
    return departamento_repository.create(db, departamento)


def atualizar(db: Session, departamento_id: int, dados: DepartamentoUpdate) -> Departamento:
    departamento = obter(db, departamento_id)
    novos_dados = dados.model_dump(exclude_unset=True)

    novo_nome = novos_dados.get("nome")
    if novo_nome and novo_nome != departamento.nome:
        existente = departamento_repository.get_by_nome(db, novo_nome)
        if existente and existente.id != departamento.id:
            raise RegraNegocioError(
                f"Já existe um departamento com o nome '{novo_nome}'", code="NOME_DUPLICADO"
            )

    for campo, valor in novos_dados.items():
        setattr(departamento, campo, valor)
    return departamento_repository.update(db, departamento)


def inativar(db: Session, departamento_id: int) -> Departamento:
    departamento = obter(db, departamento_id)
    departamento.status = StatusCadastro.INATIVO
    return departamento_repository.update(db, departamento)


def ativar(db: Session, departamento_id: int) -> Departamento:
    departamento = obter(db, departamento_id)
    departamento.status = StatusCadastro.ATIVO
    return departamento_repository.update(db, departamento)
