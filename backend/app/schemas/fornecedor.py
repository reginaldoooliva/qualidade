from pydantic import BaseModel, ConfigDict

from app.models.peca import StatusCadastro


class FornecedorBase(BaseModel):
    codigo: str
    nome: str
    cnpj: str | None = None


class FornecedorCreate(FornecedorBase):
    pass


class FornecedorUpdate(BaseModel):
    codigo: str | None = None
    nome: str | None = None
    cnpj: str | None = None
    status: StatusCadastro | None = None


class FornecedorRead(FornecedorBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: StatusCadastro
