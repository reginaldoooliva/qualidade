from sqlalchemy import Enum, LargeBinary, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin
from app.models.peca import StatusCadastro


class TipoInstrumento(TimestampMixin, Base):
    __tablename__ = "tipos_instrumento"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(150), unique=True, nullable=False, index=True)
    descricao_funcao: Mapped[str | None] = mapped_column(Text, nullable=True)
    imagem_conteudo: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    imagem_nome_arquivo: Mapped[str | None] = mapped_column(String(255), nullable=True)
    imagem_content_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[StatusCadastro] = mapped_column(
        Enum(StatusCadastro, name="status_tipo_instrumento"), nullable=False, default=StatusCadastro.ATIVO
    )

    @property
    def tem_imagem(self) -> bool:
        return self.imagem_conteudo is not None
