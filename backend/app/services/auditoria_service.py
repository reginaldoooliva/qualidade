from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.auditoria import LogAuditoria
from app.models.usuario import Usuario


def registrar(
    db: Session, entidade: str, entidade_id: int, acao: str, usuario: Usuario, detalhe: str | None = None
) -> None:
    log = LogAuditoria(entidade=entidade, entidade_id=entidade_id, acao=acao, usuario_id=usuario.id, detalhe=detalhe)
    db.add(log)
    db.commit()


def listar_por_entidade(db: Session, entidade: str, entidade_id: int) -> list[LogAuditoria]:
    stmt = (
        select(LogAuditoria)
        .where(LogAuditoria.entidade == entidade, LogAuditoria.entidade_id == entidade_id)
        .options(selectinload(LogAuditoria.usuario))
        .order_by(LogAuditoria.criado_em)
    )
    return list(db.scalars(stmt))
