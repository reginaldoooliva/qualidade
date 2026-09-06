from pydantic import BaseModel

from app.schemas.usuario import UsuarioRead


class LoginRequest(BaseModel):
    login: str
    senha: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioRead
