from pydantic import BaseModel, ConfigDict

from app.core.permissions import Perfil
from app.models.usuario import StatusUsuario


class UsuarioBase(BaseModel):
    nome: str
    login: str
    perfil: Perfil


class UsuarioCreate(UsuarioBase):
    senha: str


class UsuarioRead(UsuarioBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: StatusUsuario
