from fastapi import APIRouter

from app.api.v1 import (
    analise,
    auth,
    caracteristicas,
    coletas,
    etapas,
    nao_conformidades,
    ordens,
    pecas,
    planos_acao,
    relatorios,
    usuarios,
)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(pecas.router)
api_router.include_router(etapas.router)
api_router.include_router(caracteristicas.router)
api_router.include_router(ordens.router)
api_router.include_router(coletas.router)
api_router.include_router(analise.router)
api_router.include_router(usuarios.router)
api_router.include_router(nao_conformidades.router)
api_router.include_router(planos_acao.router)
api_router.include_router(relatorios.router)
