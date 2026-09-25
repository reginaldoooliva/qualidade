from pydantic import BaseModel, ConfigDict

from app.models.peca import StatusCadastro


class MaquinaBase(BaseModel):
    codigo: str
    descricao: str


class MaquinaCreate(MaquinaBase):
    pass


class MaquinaUpdate(BaseModel):
    codigo: str | None = None
    descricao: str | None = None
    status: StatusCadastro | None = None


class MaquinaRead(MaquinaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: StatusCadastro
