from fastapi import APIRouter

from app.api.v1 import (
    acoes_departamentais,
    analise,
    auth,
    caracteristicas,
    coletas,
    departamentos,
    deposito_qualidade,
    etapas,
    fornecedores,
    maquinas,
    nao_conformidades,
    ordens,
    pecas,
    planos_acao,
    relatorios,
    tipos_instrumento,
    usuarios,
)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(pecas.router)
api_router.include_router(fornecedores.router)
api_router.include_router(maquinas.router)
api_router.include_router(departamentos.router)
api_router.include_router(tipos_instrumento.router)
api_router.include_router(etapas.router)
api_router.include_router(caracteristicas.router)
api_router.include_router(ordens.router)
api_router.include_router(coletas.router)
api_router.include_router(analise.router)
api_router.include_router(usuarios.router)
api_router.include_router(nao_conformidades.router)
api_router.include_router(acoes_departamentais.router)
api_router.include_router(planos_acao.router)
api_router.include_router(relatorios.router)
api_router.include_router(deposito_qualidade.router)
