from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import NaoAutorizadoError, RecursoNaoEncontradoError, RegraNegocioError
from app.core.permissions import PERFIS_QUALIDADE
from app.models.nao_conformidade import AcaoDepartamental, StatusAcaoDepartamental
from app.models.usuario import Usuario
from app.repositories import acao_departamental_repository, departamento_repository
from app.schemas.nao_conformidade import AcaoDepartamentalConcluirRequest, AcaoDepartamentalCreate
from app.services import auditoria_service, nao_conformidade_service


def adicionar(db: Session, nc_id: int, dados: AcaoDepartamentalCreate, usuario: Usuario) -> AcaoDepartamental:
    nc = nao_conformidade_service.obter(db, nc_id)
    departamento = departamento_repository.get_by_id(db, dados.departamento_id)
    if not departamento:
        raise RecursoNaoEncontradoError(f"Departamento {dados.departamento_id} não encontrado")

    acao = AcaoDepartamental(
        nc_id=nc.id,
        departamento_id=departamento.id,
        descricao=dados.descricao,
        status=StatusAcaoDepartamental.PENDENTE,
        criado_por_id=usuario.id,
    )
    acao = acao_departamental_repository.create(db, acao)
    auditoria_service.registrar(
        db,
        entidade="nao_conformidade",
        entidade_id=nc.id,
        acao="acao_departamental_criada",
        usuario=usuario,
        detalhe=f"Tratativa para {departamento.nome}: {dados.descricao}",
    )
    return acao


def _obter(db: Session, nc_id: int, acao_id: int) -> AcaoDepartamental:
    acao = acao_departamental_repository.get_by_id(db, acao_id)
    if not acao or acao.nc_id != nc_id:
        raise RecursoNaoEncontradoError(f"Tratativa departamental {acao_id} não encontrada para esta RNC")
    return acao


def remover(db: Session, nc_id: int, acao_id: int, usuario: Usuario) -> None:
    acao = _obter(db, nc_id, acao_id)
    if acao.status != StatusAcaoDepartamental.PENDENTE:
        raise RegraNegocioError(
            "Só é possível remover tratativas ainda pendentes", code="ACAO_DEPARTAMENTAL_JA_CONCLUIDA"
        )
    departamento_nome = acao.departamento.nome
    acao_departamental_repository.delete(db, acao)
    auditoria_service.registrar(
        db,
        entidade="nao_conformidade",
        entidade_id=nc_id,
        acao="acao_departamental_removida",
        usuario=usuario,
        detalhe=f"Tratativa para {departamento_nome} removida",
    )


def concluir(
    db: Session, nc_id: int, acao_id: int, dados: AcaoDepartamentalConcluirRequest, usuario: Usuario
) -> AcaoDepartamental:
    acao = _obter(db, nc_id, acao_id)
    pode_concluir = usuario.perfil in PERFIS_QUALIDADE or (
        usuario.departamento_id is not None and usuario.departamento_id == acao.departamento_id
    )
    if not pode_concluir:
        raise NaoAutorizadoError("Só um usuário do departamento responsável (ou a Qualidade) pode concluir esta tratativa")
    if acao.status == StatusAcaoDepartamental.CONCLUIDA:
        raise RegraNegocioError("Esta tratativa já está concluída", code="ACAO_DEPARTAMENTAL_JA_CONCLUIDA")

    acao.status = StatusAcaoDepartamental.CONCLUIDA
    acao.observacao_conclusao = dados.observacao
    acao.concluido_por_id = usuario.id
    acao.concluido_em = datetime.now(timezone.utc)
    acao = acao_departamental_repository.update(db, acao)
    auditoria_service.registrar(
        db,
        entidade="nao_conformidade",
        entidade_id=nc_id,
        acao="acao_departamental_concluida",
        usuario=usuario,
        detalhe=f"Tratativa para {acao.departamento.nome} concluída: {dados.observacao}",
    )
    return acao


def listar_pendentes(db: Session, departamento_id: int | None = None) -> list[AcaoDepartamental]:
    return acao_departamental_repository.list_pendentes(db, departamento_id=departamento_id)
