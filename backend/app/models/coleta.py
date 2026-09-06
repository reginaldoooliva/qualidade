import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class StatusRodada(str, enum.Enum):
    EM_ANDAMENTO = "em_andamento"
    FINALIZADA = "finalizada"
    FINALIZADA_COM_PENDENCIA = "finalizada_com_pendencia"


class MotivoEncerramento(str, enum.Enum):
    ORDEM_INTERROMPIDA = "ordem_interrompida"
    ORDEM_CANCELADA = "ordem_cancelada"
    QUANTIDADE_MENOR_QUE_PREVISTO = "quantidade_menor_que_previsto"
    NAO_CONFORMIDADE_PROCESSO = "nao_conformidade_processo"
    OUTRO = "outro"


class RodadaColeta(TimestampMixin, Base):
    __tablename__ = "rodadas_coleta"
    __table_args__ = (UniqueConstraint("ordem_id", "etapa_id", name="uq_rodada_ordem_etapa"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    ordem_id: Mapped[int] = mapped_column(ForeignKey("ordens_producao.id", ondelete="RESTRICT"), nullable=False)
    etapa_id: Mapped[int] = mapped_column(ForeignKey("etapas.id", ondelete="RESTRICT"), nullable=False)
    amostras_calculadas: Mapped[int] = mapped_column(nullable=False)
    amostras_ajustadas: Mapped[int | None] = mapped_column(nullable=True)
    justificativa_ajuste: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[StatusRodada] = mapped_column(
        Enum(StatusRodada, name="status_rodada"), nullable=False, default=StatusRodada.EM_ANDAMENTO
    )
    motivo_encerramento_antecipado: Mapped[MotivoEncerramento | None] = mapped_column(
        Enum(MotivoEncerramento, name="motivo_encerramento"), nullable=True
    )
    motivo_detalhe: Mapped[str | None] = mapped_column(Text, nullable=True)
    data_hora_inicio: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    ordem: Mapped["OrdemProducao"] = relationship()  # noqa: F821
    etapa: Mapped["Etapa"] = relationship()  # noqa: F821
    medicoes: Mapped[list["Medicao"]] = relationship(back_populates="rodada", cascade="all, delete-orphan")

    @property
    def amostras_alvo(self) -> int:
        return self.amostras_ajustadas if self.amostras_ajustadas is not None else self.amostras_calculadas

    @property
    def peca(self) -> "Peca":  # noqa: F821
        return self.ordem.peca

    @property
    def numero_ordem(self) -> str:
        return self.ordem.numero_ordem

    @property
    def caracteristicas(self) -> list["Caracteristica"]:  # noqa: F821
        return self.etapa.caracteristicas


class Medicao(Base):
    __tablename__ = "medicoes"
    __table_args__ = (
        UniqueConstraint("rodada_id", "caracteristica_id", "amostra_numero", name="uq_medicao_amostra"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    rodada_id: Mapped[int] = mapped_column(ForeignKey("rodadas_coleta.id", ondelete="CASCADE"), nullable=False)
    caracteristica_id: Mapped[int] = mapped_column(
        ForeignKey("caracteristicas.id", ondelete="RESTRICT"), nullable=False
    )
    amostra_numero: Mapped[int] = mapped_column(nullable=False)
    valor: Mapped[float] = mapped_column(Numeric(12, 5), nullable=False)
    operador_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False)
    data_hora: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    rodada: Mapped["RodadaColeta"] = relationship(back_populates="medicoes")
    caracteristica: Mapped["Caracteristica"] = relationship()  # noqa: F821
    operador: Mapped["Usuario"] = relationship()  # noqa: F821

    @property
    def operador_nome(self) -> str:
        return self.operador.nome
