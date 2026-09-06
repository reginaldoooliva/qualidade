from pydantic import BaseModel, ConfigDict, Field

from app.models.peca import InstrumentoMedicao, StatusCadastro, UnidadeMedida


class CaracteristicaBase(BaseModel):
    nome: str
    posicao_desenho: str | None = None
    nominal: float
    tol_superior: float = Field(ge=0)
    tol_inferior: float = Field(ge=0)
    unidade: UnidadeMedida = UnidadeMedida.MM
    instrumento: InstrumentoMedicao | None = None
    casas_decimais: int = Field(default=3, ge=0, le=6)


class CaracteristicaCreate(CaracteristicaBase):
    pass


class CaracteristicaUpdate(BaseModel):
    nome: str | None = None
    posicao_desenho: str | None = None
    nominal: float | None = None
    tol_superior: float | None = Field(default=None, ge=0)
    tol_inferior: float | None = Field(default=None, ge=0)
    unidade: UnidadeMedida | None = None
    instrumento: InstrumentoMedicao | None = None
    casas_decimais: int | None = Field(default=None, ge=0, le=6)
    status: StatusCadastro | None = None


class CaracteristicaRead(CaracteristicaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    etapa_id: int
    status: StatusCadastro
    lse: float
    lie: float
