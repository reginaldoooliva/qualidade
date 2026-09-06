from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models.usuario import Usuario
from app.schemas.auth import LoginRequest, Token
from app.schemas.usuario import UsuarioRead
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
def login(dados: LoginRequest, db: Session = Depends(get_db)) -> Token:
    return auth_service.autenticar(db, dados.login, dados.senha)


@router.get("/me", response_model=UsuarioRead)
def me(usuario: Usuario = Depends(get_current_user)) -> Usuario:
    return usuario
