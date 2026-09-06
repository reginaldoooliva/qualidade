from sqlalchemy.orm import Session

from app.core.exceptions import RecursoNaoEncontradoError, RegraNegocioError
from app.models.peca import Peca, StatusCadastro
from app.repositories import peca_repository
from app.schemas.peca import PecaCreate, PecaListItem, PecaUpdate


def listar(db: Session, busca: str | None = None, cliente: str | None = None) -> list[PecaListItem]:
    pecas = peca_repository.list_pecas(db, busca=busca, cliente=cliente)
    itens = []
    for peca in pecas:
        item = PecaListItem.model_validate(peca)
        item.numero_caracteristicas = peca_repository.contar_caracteristicas(db, peca.id)
        itens.append(item)
    return itens


def obter(db: Session, peca_id: int) -> Peca:
    peca = peca_repository.get_by_id(db, peca_id)
    if not peca:
        raise RecursoNaoEncontradoError(f"Peça {peca_id} não encontrada")
    return peca


def criar(db: Session, dados: PecaCreate) -> Peca:
    if peca_repository.get_by_codigo(db, dados.codigo):
        raise RegraNegocioError(f"Já existe uma peça com o código '{dados.codigo}'", code="CODIGO_DUPLICADO")
    peca = Peca(**dados.model_dump())
    return peca_repository.create(db, peca)


def atualizar(db: Session, peca_id: int, dados: PecaUpdate) -> Peca:
    peca = obter(db, peca_id)
    novos_dados = dados.model_dump(exclude_unset=True)

    novo_codigo = novos_dados.get("codigo")
    if novo_codigo and novo_codigo != peca.codigo:
        existente = peca_repository.get_by_codigo(db, novo_codigo)
        if existente and existente.id != peca.id:
            raise RegraNegocioError(f"Já existe uma peça com o código '{novo_codigo}'", code="CODIGO_DUPLICADO")

    for campo, valor in novos_dados.items():
        setattr(peca, campo, valor)
    return peca_repository.update(db, peca)


def inativar(db: Session, peca_id: int) -> Peca:
    peca = obter(db, peca_id)
    peca.status = StatusCadastro.INATIVO
    return peca_repository.update(db, peca)


def ativar(db: Session, peca_id: int) -> Peca:
    peca = obter(db, peca_id)
    peca.status = StatusCadastro.ATIVO
    return peca_repository.update(db, peca)
