from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.coleta import MotivoEncerramento, StatusRodada
from app.schemas.caracteristica import CaracteristicaRead
from app.schemas.etapa import EtapaRead
from app.schemas.peca import PecaRead


class OrdemProducaoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    peca_id: int
    numero_ordem: str
    quantidade: int


class IniciarColetaRequest(BaseModel):
    peca_id: int
    numero_ordem: str
    quantidade_ordem: int | None = Field(default=None, ge=1)
    etapa_id: int
    amostras_ajustadas: int | None = Field(default=None, ge=1)
    justificativa_ajuste: str | None = None


class MedicaoUpsert(BaseModel):
    valor: float


class MedicaoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    caracteristica_id: int
    amostra_numero: int
    valor: float
    operador_id: int
    operador_nome: str
    data_hora: datetime


class RodadaColetaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ordem_id: int
    etapa_id: int
    amostras_calculadas: int
    amostras_ajustadas: int | None
    amostras_alvo: int
    justificativa_ajuste: str | None
    status: StatusRodada
    motivo_encerramento_antecipado: MotivoEncerramento | None
    motivo_detalhe: str | None
    data_hora_inicio: datetime


class RodadaColetaDetalhe(RodadaColetaRead):
    peca: PecaRead
    etapa: EtapaRead
    ordem: OrdemProducaoRead
    caracteristicas: list[CaracteristicaRead]
    medicoes: list[MedicaoRead]


class FinalizarColetaRequest(BaseModel):
    motivo_encerramento_antecipado: MotivoEncerramento | None = None
    motivo_detalhe: str | None = None


class FinalizarColetaResponse(RodadaColetaRead):
    sugestao_abrir_rnc: bool = False
