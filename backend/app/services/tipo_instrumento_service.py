from sqlalchemy.orm import Session

from app.core.exceptions import RecursoNaoEncontradoError, RegraNegocioError
from app.models.peca import StatusCadastro
from app.models.tipo_instrumento import TipoInstrumento
from app.repositories import tipo_instrumento_repository
from app.schemas.tipo_instrumento import TipoInstrumentoCreate, TipoInstrumentoUpdate

TIPOS_IMAGEM_PERMITIDOS = {"image/jpeg", "image/png", "image/webp"}
TAMANHO_MAXIMO_IMAGEM_BYTES = 5 * 1024 * 1024


def listar(
    db: Session, busca: str | None = None, status: StatusCadastro | None = None
) -> list[TipoInstrumento]:
    return tipo_instrumento_repository.list_tipos(db, busca=busca, status=status)


def obter(db: Session, tipo_id: int) -> TipoInstrumento:
    tipo = tipo_instrumento_repository.get_by_id(db, tipo_id)
    if not tipo:
        raise RecursoNaoEncontradoError(f"Tipo de instrumento {tipo_id} não encontrado")
    return tipo


def criar(db: Session, dados: TipoInstrumentoCreate) -> TipoInstrumento:
    if tipo_instrumento_repository.get_by_nome(db, dados.nome):
        raise RegraNegocioError(
            f"Já existe um tipo de instrumento com o nome '{dados.nome}'", code="NOME_DUPLICADO"
        )
    tipo = TipoInstrumento(**dados.model_dump())
    return tipo_instrumento_repository.create(db, tipo)


def atualizar(db: Session, tipo_id: int, dados: TipoInstrumentoUpdate) -> TipoInstrumento:
    tipo = obter(db, tipo_id)
    novos_dados = dados.model_dump(exclude_unset=True)

    novo_nome = novos_dados.get("nome")
    if novo_nome and novo_nome != tipo.nome:
        existente = tipo_instrumento_repository.get_by_nome(db, novo_nome)
        if existente and existente.id != tipo.id:
            raise RegraNegocioError(
                f"Já existe um tipo de instrumento com o nome '{novo_nome}'", code="NOME_DUPLICADO"
            )

    for campo, valor in novos_dados.items():
        setattr(tipo, campo, valor)
    return tipo_instrumento_repository.update(db, tipo)


def inativar(db: Session, tipo_id: int) -> TipoInstrumento:
    tipo = obter(db, tipo_id)
    tipo.status = StatusCadastro.INATIVO
    return tipo_instrumento_repository.update(db, tipo)


def ativar(db: Session, tipo_id: int) -> TipoInstrumento:
    tipo = obter(db, tipo_id)
    tipo.status = StatusCadastro.ATIVO
    return tipo_instrumento_repository.update(db, tipo)


def anexar_imagem(
    db: Session, tipo_id: int, nome_arquivo: str, content_type: str, conteudo: bytes
) -> TipoInstrumento:
    tipo = obter(db, tipo_id)
    if content_type not in TIPOS_IMAGEM_PERMITIDOS:
        raise RegraNegocioError(
            "Formato de imagem não suportado. Envie JPEG, PNG ou WEBP.", code="IMAGEM_FORMATO_INVALIDO"
        )
    if len(conteudo) > TAMANHO_MAXIMO_IMAGEM_BYTES:
        raise RegraNegocioError("A imagem excede o tamanho máximo de 5 MB.", code="IMAGEM_TAMANHO_EXCEDIDO")

    tipo.imagem_conteudo = conteudo
    tipo.imagem_nome_arquivo = nome_arquivo
    tipo.imagem_content_type = content_type
    return tipo_instrumento_repository.update(db, tipo)
