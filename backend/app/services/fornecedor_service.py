from sqlalchemy.orm import Session

from app.core.exceptions import RecursoNaoEncontradoError, RegraNegocioError
from app.models.fornecedor import Fornecedor
from app.models.peca import StatusCadastro
from app.repositories import fornecedor_repository
from app.schemas.fornecedor import FornecedorCreate, FornecedorUpdate


def listar(db: Session, busca: str | None = None) -> list[Fornecedor]:
    return fornecedor_repository.list_fornecedores(db, busca=busca)


def obter(db: Session, fornecedor_id: int) -> Fornecedor:
    fornecedor = fornecedor_repository.get_by_id(db, fornecedor_id)
    if not fornecedor:
        raise RecursoNaoEncontradoError(f"Fornecedor {fornecedor_id} não encontrado")
    return fornecedor


def criar(db: Session, dados: FornecedorCreate) -> Fornecedor:
    if fornecedor_repository.get_by_codigo(db, dados.codigo):
        raise RegraNegocioError(
            f"Já existe um fornecedor com o código '{dados.codigo}'", code="CODIGO_DUPLICADO"
        )
    fornecedor = Fornecedor(**dados.model_dump())
    return fornecedor_repository.create(db, fornecedor)


def atualizar(db: Session, fornecedor_id: int, dados: FornecedorUpdate) -> Fornecedor:
    fornecedor = obter(db, fornecedor_id)
    novos_dados = dados.model_dump(exclude_unset=True)

    novo_codigo = novos_dados.get("codigo")
    if novo_codigo and novo_codigo != fornecedor.codigo:
        existente = fornecedor_repository.get_by_codigo(db, novo_codigo)
        if existente and existente.id != fornecedor.id:
            raise RegraNegocioError(
                f"Já existe um fornecedor com o código '{novo_codigo}'", code="CODIGO_DUPLICADO"
            )

    for campo, valor in novos_dados.items():
        setattr(fornecedor, campo, valor)
    return fornecedor_repository.update(db, fornecedor)


def inativar(db: Session, fornecedor_id: int) -> Fornecedor:
    fornecedor = obter(db, fornecedor_id)
    fornecedor.status = StatusCadastro.INATIVO
    return fornecedor_repository.update(db, fornecedor)


def ativar(db: Session, fornecedor_id: int) -> Fornecedor:
    fornecedor = obter(db, fornecedor_id)
    fornecedor.status = StatusCadastro.ATIVO
    return fornecedor_repository.update(db, fornecedor)
