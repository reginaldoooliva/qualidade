from datetime import datetime

from pydantic import BaseModel

from app.models.peca import UnidadeMedida
from app.schemas.analise import OperadorResumo, RodadaResumo


class SubgrupoCarta(BaseModel):
    rodada_id: int
    numero_ordem: str
    data_hora_inicio: datetime
    n: int
    media: float
    amplitude: float
    fora_controle_x: bool
    fora_controle_r: bool


class CartaControleCaracteristica(BaseModel):
    caracteristica_id: int
    nome: str
    unidade: UnidadeMedida
    casas_decimais: int
    subgrupos: list[SubgrupoCarta]
    exibir: bool
    tamanho_amostra_medio: float | None
    linha_central_x: float | None
    lsc_x: float | None
    lic_x: float | None
    linha_central_r: float | None
    lsc_r: float | None
    lic_r: float | None


class CartaControleResponse(BaseModel):
    peca_id: int
    peca_codigo: str
    etapa_id: int
    etapa_numero: int
    rodadas_incluidas: list[RodadaResumo]
    operadores_disponiveis: list[OperadorResumo]
    caracteristicas: list[CartaControleCaracteristica]
