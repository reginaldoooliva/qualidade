from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class OrdemProducao(TimestampMixin, Base):
    __tablename__ = "ordens_producao"
    __table_args__ = (UniqueConstraint("peca_id", "numero_ordem", name="uq_ordem_peca_numero"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    peca_id: Mapped[int] = mapped_column(ForeignKey("pecas.id", ondelete="RESTRICT"), nullable=False)
    numero_ordem: Mapped[str] = mapped_column(String(60), nullable=False)
    quantidade: Mapped[int] = mapped_column(nullable=False)

    peca: Mapped["Peca"] = relationship()  # noqa: F821
