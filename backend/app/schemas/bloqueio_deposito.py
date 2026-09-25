from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.bloqueio_deposito import StatusBloqueioDeposito
from app.schemas.peca import PecaRead


class BloqueioDepositoCreate(BaseModel):
    peca_id: int
    motivo: str = Field(min_length=1)
    caracteristica_atencao: str | None = None
    cliente: str | None = None
    nao_conformidade_id: int | None = None


class BloqueioDepositoLiberar(BaseModel):
    observacao_liberacao: str = Field(min_length=1)


class BloqueioDepositoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    peca_id: int
    peca: PecaRead
    nao_conformidade_id: int | None
    motivo: str
    caracteristica_atencao: str | None
    cliente: str | None
    status: StatusBloqueioDeposito
    criado_por_id: int
    criado_por_nome: str
    liberado_por_id: int | None
    liberado_por_nome: str | None
    data_liberacao: datetime | None
    observacao_liberacao: str | None
    tem_foto: bool
    criado_em: datetime


class PecaComBloqueiosRead(BaseModel):
    peca: PecaRead
    bloqueios: list[BloqueioDepositoRead]
