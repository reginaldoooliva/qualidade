from pydantic import BaseModel


class ItemConsolidadoPeca(BaseModel):
    peca_id: int
    codigo: str
    descricao: str
    caracteristica_critica: str | None
    etapa_numero: int | None
    cpk_critico: float | None
    classificacao: str | None
    n_amostras: int


class ConsolidadoNaoConformidade(BaseModel):
    total_rnc: int
    total_encerradas: int
    tempo_medio_tratamento_dias: float | None
    taxa_reincidencia: float
    por_peca: dict[str, int]
    por_classificacao: dict[str, int]
    por_origem: dict[str, int]
