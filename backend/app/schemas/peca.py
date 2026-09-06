from pydantic import BaseModel, ConfigDict

from app.models.peca import StatusCadastro


class PecaBase(BaseModel):
    codigo: str
    descricao: str
    cliente: str | None = None
    desenho: str | None = None
    revisao: str
    material: str | None = None
    observacoes: str | None = None


class PecaCreate(PecaBase):
    pass


class PecaUpdate(BaseModel):
    codigo: str | None = None
    descricao: str | None = None
    cliente: str | None = None
    desenho: str | None = None
    revisao: str | None = None
    material: str | None = None
    observacoes: str | None = None
    status: StatusCadastro | None = None


class PecaRead(PecaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: StatusCadastro


class PecaListItem(PecaRead):
    numero_caracteristicas: int = 0
