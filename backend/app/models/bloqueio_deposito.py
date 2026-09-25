import enum
from datetime import datetime

from sqlalchemy import Enum, ForeignKey, LargeBinary, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class StatusBloqueioDeposito(str, enum.Enum):
    BLOQUEADO = "bloqueado"
    LIBERADO = "liberado"


class BloqueioDeposito(TimestampMixin, Base):
    __tablename__ = "bloqueios_deposito"

    id: Mapped[int] = mapped_column(primary_key=True)
    peca_id: Mapped[int] = mapped_column(ForeignKey("pecas.id", ondelete="RESTRICT"), nullable=False, index=True)
    nao_conformidade_id: Mapped[int | None] = mapped_column(
        ForeignKey("nao_conformidades.id", ondelete="SET NULL"), nullable=True
    )

    motivo: Mapped[str] = mapped_column(Text, nullable=False)
    caracteristica_atencao: Mapped[str | None] = mapped_column(Text, nullable=True)
    cliente: Mapped[str | None] = mapped_column(String(200), nullable=True)

    status: Mapped[StatusBloqueioDeposito] = mapped_column(
        Enum(StatusBloqueioDeposito, name="status_bloqueio_deposito"),
        nullable=False,
        default=StatusBloqueioDeposito.BLOQUEADO,
        index=True,
    )

    criado_por_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False)
    liberado_por_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=True)
    data_liberacao: Mapped[datetime | None] = mapped_column(nullable=True)
    observacao_liberacao: Mapped[str | None] = mapped_column(Text, nullable=True)

    foto_conteudo: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    foto_nome_arquivo: Mapped[str | None] = mapped_column(String(255), nullable=True)
    foto_content_type: Mapped[str | None] = mapped_column(String(100), nullable=True)

    peca: Mapped["Peca"] = relationship()  # noqa: F821
    nao_conformidade: Mapped["NaoConformidade | None"] = relationship()  # noqa: F821
    criado_por: Mapped["Usuario"] = relationship(foreign_keys=[criado_por_id])  # noqa: F821
    liberado_por: Mapped["Usuario | None"] = relationship(foreign_keys=[liberado_por_id])  # noqa: F821

    @property
    def criado_por_nome(self) -> str:
        return self.criado_por.nome

    @property
    def liberado_por_nome(self) -> str | None:
        return self.liberado_por.nome if self.liberado_por else None

    @property
    def tem_foto(self) -> bool:
        return self.foto_conteudo is not None
