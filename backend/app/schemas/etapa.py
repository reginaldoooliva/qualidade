from pydantic import BaseModel, ConfigDict, Field

from app.models.peca import StatusCadastro
from app.schemas.caracteristica import CaracteristicaRead


class EtapaBase(BaseModel):
    numero_etapa: int
    descricao: str | None = None
    freq_numerador: int = Field(default=1, ge=1)
    freq_denominador: int = Field(default=1, ge=1)


class EtapaCreate(EtapaBase):
    pass


class EtapaUpdate(BaseModel):
    numero_etapa: int | None = None
    descricao: str | None = None
    freq_numerador: int | None = Field(default=None, ge=1)
    freq_denominador: int | None = Field(default=None, ge=1)
    status: StatusCadastro | None = None


class EtapaRead(EtapaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    peca_id: int
    status: StatusCadastro


class EtapaComCaracteristicas(EtapaRead):
    caracteristicas: list[CaracteristicaRead] = []
