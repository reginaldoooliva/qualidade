from pydantic import BaseModel, ConfigDict

from app.core.permissions import Perfil
from app.models.usuario import StatusUsuario
from app.schemas.departamento import DepartamentoRead


class UsuarioBase(BaseModel):
    nome: str
    login: str
    perfil: Perfil


class UsuarioCreate(UsuarioBase):
    senha: str
    departamento_id: int | None = None


class UsuarioRead(UsuarioBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: StatusUsuario
    departamento_id: int | None = None
    departamento: DepartamentoRead | None = None


class AtualizarDepartamentoRequest(BaseModel):
    departamento_id: int | None = None
