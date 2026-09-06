import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.plano_acao import StatusPlanoAcao


class StatusNC(str, enum.Enum):
    ABERTA = "aberta"
    EM_ANALISE = "em_analise"
    EM_TRATAMENTO = "em_tratamento"
    ENCERRADA = "encerrada"


class ClassificacaoNC(str, enum.Enum):
    CRITICA = "critica"
    MAIOR = "maior"
    MENOR = "menor"


class OrigemNC(str, enum.Enum):
    PROCESSO = "processo"
    MATERIA_PRIMA = "materia_prima"
    PROJETO = "projeto"
    INSTRUMENTO = "instrumento"
    MAO_DE_OBRA = "mao_de_obra"
    OUTRO = "outro"


class DisposicaoNC(str, enum.Enum):
    RETRABALHO = "retrabalho"
    SUCATA = "sucata"
    USO_COMO_ESTA = "uso_como_esta"
    DEVOLUCAO_FORNECEDOR = "devolucao_fornecedor"
    RECLASSIFICACAO = "reclassificacao"


class NaoConformidade(TimestampMixin, Base):
    __tablename__ = "nao_conformidades"

    id: Mapped[int] = mapped_column(primary_key=True)
    numero_rnc: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)

    peca_id: Mapped[int] = mapped_column(ForeignKey("pecas.id", ondelete="RESTRICT"), nullable=False)
    ordem_id: Mapped[int | None] = mapped_column(ForeignKey("ordens_producao.id", ondelete="SET NULL"), nullable=True)
    etapa_id: Mapped[int | None] = mapped_column(ForeignKey("etapas.id", ondelete="SET NULL"), nullable=True)
    caracteristica_id: Mapped[int | None] = mapped_column(
        ForeignKey("caracteristicas.id", ondelete="SET NULL"), nullable=True
    )
    rodada_id: Mapped[int | None] = mapped_column(
        ForeignKey("rodadas_coleta.id", ondelete="SET NULL"), nullable=True
    )

    descricao_problema: Mapped[str] = mapped_column(Text, nullable=False)
    quantidade_afetada: Mapped[int] = mapped_column(nullable=False)
    classificacao: Mapped[ClassificacaoNC] = mapped_column(Enum(ClassificacaoNC, name="classificacao_nc"), nullable=False)
    origem: Mapped[OrigemNC] = mapped_column(Enum(OrigemNC, name="origem_nc"), nullable=False)

    causa_raiz_preliminar: Mapped[str | None] = mapped_column(Text, nullable=True)
    disposicao: Mapped[DisposicaoNC | None] = mapped_column(Enum(DisposicaoNC, name="disposicao_nc"), nullable=True)
    responsavel_analise_id: Mapped[int | None] = mapped_column(
        ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=True
    )
    necessita_plano_acao: Mapped[bool] = mapped_column(nullable=False, default=False)

    aberto_por_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False)
    data_abertura: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    data_encerramento: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[StatusNC] = mapped_column(Enum(StatusNC, name="status_nc"), nullable=False, default=StatusNC.ABERTA)

    peca: Mapped["Peca"] = relationship()  # noqa: F821
    ordem: Mapped["OrdemProducao | None"] = relationship()  # noqa: F821
    etapa: Mapped["Etapa | None"] = relationship()  # noqa: F821
    caracteristica: Mapped["Caracteristica | None"] = relationship()  # noqa: F821
    rodada: Mapped["RodadaColeta | None"] = relationship()  # noqa: F821
    aberto_por: Mapped["Usuario"] = relationship(foreign_keys=[aberto_por_id])  # noqa: F821
    responsavel_analise: Mapped["Usuario | None"] = relationship(foreign_keys=[responsavel_analise_id])  # noqa: F821
    planos_acao: Mapped[list["PlanoDeAcao"]] = relationship(  # noqa: F821
        back_populates="nao_conformidade", order_by="PlanoDeAcao.id"
    )

    @property
    def aberto_por_nome(self) -> str:
        return self.aberto_por.nome

    @property
    def plano_acao_ativo(self) -> "PlanoDeAcao | None":  # noqa: F821
        for plano in self.planos_acao:
            if plano.status != StatusPlanoAcao.ENCERRADO:
                return plano
        return None

    @property
    def tem_plano_aberto(self) -> bool:
        return self.status == StatusNC.ENCERRADA and self.plano_acao_ativo is not None
