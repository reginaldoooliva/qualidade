from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import RecursoNaoEncontradoError, RegraNegocioError
from app.models.bloqueio_deposito import BloqueioDeposito, StatusBloqueioDeposito
from app.models.peca import Peca
from app.models.usuario import Usuario
from app.repositories import bloqueio_deposito_repository, nao_conformidade_repository, peca_repository
from app.schemas.bloqueio_deposito import BloqueioDepositoCreate, BloqueioDepositoLiberar
from app.services import auditoria_service

TIPOS_FOTO_PERMITIDOS = {"image/jpeg", "image/png", "image/webp"}
TAMANHO_MAXIMO_FOTO_BYTES = 5 * 1024 * 1024


def obter(db: Session, bloqueio_id: int) -> BloqueioDeposito:
    bloqueio = bloqueio_deposito_repository.get_by_id(db, bloqueio_id)
    if not bloqueio:
        raise RecursoNaoEncontradoError(f"Bloqueio {bloqueio_id} não encontrado")
    return bloqueio


def listar(
    db: Session, status: StatusBloqueioDeposito | None = None, busca: str | None = None
) -> list[BloqueioDeposito]:
    return bloqueio_deposito_repository.list_all(db, status=status, busca=busca)


def buscar_por_codigo_peca(db: Session, codigo: str) -> tuple[Peca, list[BloqueioDeposito]]:
    peca = peca_repository.get_by_codigo(db, codigo)
    if not peca:
        raise RecursoNaoEncontradoError(f"Peça com código '{codigo}' não encontrada")
    return peca, bloqueio_deposito_repository.list_by_peca_id(db, peca.id)


def criar(db: Session, dados: BloqueioDepositoCreate, usuario: Usuario) -> BloqueioDeposito:
    peca = peca_repository.get_by_id(db, dados.peca_id)
    if not peca:
        raise RecursoNaoEncontradoError(f"Peça {dados.peca_id} não encontrada")

    if dados.nao_conformidade_id is not None:
        nc = nao_conformidade_repository.get_by_id(db, dados.nao_conformidade_id)
        if not nc:
            raise RecursoNaoEncontradoError(f"RNC {dados.nao_conformidade_id} não encontrada")

    bloqueio = BloqueioDeposito(
        peca_id=peca.id,
        nao_conformidade_id=dados.nao_conformidade_id,
        motivo=dados.motivo,
        caracteristica_atencao=dados.caracteristica_atencao,
        cliente=dados.cliente,
        criado_por_id=usuario.id,
        status=StatusBloqueioDeposito.BLOQUEADO,
    )
    bloqueio = bloqueio_deposito_repository.create(db, bloqueio)
    auditoria_service.registrar(
        db,
        entidade="bloqueio_deposito",
        entidade_id=bloqueio.id,
        acao="abertura",
        usuario=usuario,
        detalhe=f"Peça {peca.codigo} bloqueada no depósito da qualidade",
    )
    return bloqueio


def liberar(db: Session, bloqueio_id: int, dados: BloqueioDepositoLiberar, usuario: Usuario) -> BloqueioDeposito:
    bloqueio = obter(db, bloqueio_id)
    if bloqueio.status != StatusBloqueioDeposito.BLOQUEADO:
        raise RegraNegocioError("Este bloqueio já foi liberado", code="BLOQUEIO_JA_LIBERADO")

    bloqueio.status = StatusBloqueioDeposito.LIBERADO
    bloqueio.liberado_por_id = usuario.id
    bloqueio.data_liberacao = datetime.now(timezone.utc)
    bloqueio.observacao_liberacao = dados.observacao_liberacao
    bloqueio_deposito_repository.update(db, bloqueio)
    auditoria_service.registrar(
        db,
        entidade="bloqueio_deposito",
        entidade_id=bloqueio.id,
        acao="liberacao",
        usuario=usuario,
        detalhe=f"Peça {bloqueio.peca.codigo} liberada do depósito da qualidade",
    )
    return bloqueio


def anexar_foto(
    db: Session, bloqueio_id: int, nome_arquivo: str, content_type: str, conteudo: bytes, usuario: Usuario
) -> BloqueioDeposito:
    bloqueio = obter(db, bloqueio_id)
    if content_type not in TIPOS_FOTO_PERMITIDOS:
        raise RegraNegocioError(
            "Formato de imagem não suportado. Envie JPEG, PNG ou WEBP.", code="FOTO_FORMATO_INVALIDO"
        )
    if len(conteudo) > TAMANHO_MAXIMO_FOTO_BYTES:
        raise RegraNegocioError("A foto excede o tamanho máximo de 5 MB.", code="FOTO_TAMANHO_EXCEDIDO")

    bloqueio.foto_conteudo = conteudo
    bloqueio.foto_nome_arquivo = nome_arquivo
    bloqueio.foto_content_type = content_type
    return bloqueio_deposito_repository.update(db, bloqueio)
