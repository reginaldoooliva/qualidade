from pydantic import BaseModel, ConfigDict


class ErrorResponse(BaseModel):
    detail: str
    code: str


class UsuarioResumo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
