from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.coleta import StatusRodada
from app.models.peca import InstrumentoMedicao, UnidadeMedida


class OperadorResumo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str


class RodadaResumo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    numero_ordem: str
    status: StatusRodada
    data_hora_inicio: datetime


class CaracteristicaCapabilidade(BaseModel):
    caracteristica_id: int
    nome: str
    unidade: UnidadeMedida
    instrumento: InstrumentoMedicao | None
    casas_decimais: int
    nominal: float
    lie: float
    lse: float
    n_amostras: int
    media: float | None
    desvio_padrao: float | None
    cp: float | None
    cpk: float | None
    classificacao: str | None  # "nao_capaz" | "atencao" | "capaz"
    baixa_robustez: bool
    valores: list[float]


class AnaliseCapabilidadeResponse(BaseModel):
    peca_id: int
    peca_codigo: str
    etapa_id: int
    etapa_numero: int
    rodadas_incluidas: list[RodadaResumo]
    operadores_disponiveis: list[OperadorResumo]
    limiar_baixa_robustez: int
    caracteristicas: list[CaracteristicaCapabilidade]
