from pydantic import BaseModel, ConfigDict

from app.models.peca import StatusCadastro


class DepartamentoBase(BaseModel):
    nome: str


class DepartamentoCreate(DepartamentoBase):
    pass


class DepartamentoUpdate(BaseModel):
    nome: str | None = None
    status: StatusCadastro | None = None


class DepartamentoRead(DepartamentoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: StatusCadastro
