class AppError(Exception):
    """Base para exceções de domínio, convertidas em respostas HTTP padronizadas."""

    status_code = 400
    code = "ERRO"

    def __init__(self, detail: str, code: str | None = None):
        self.detail = detail
        if code:
            self.code = code
        super().__init__(detail)


class RegraNegocioError(AppError):
    status_code = 400
    code = "REGRA_NEGOCIO"


class ConflitoEstadoError(AppError):
    status_code = 409
    code = "CONFLITO_ESTADO"


class RecursoNaoEncontradoError(AppError):
    status_code = 404
    code = "NAO_ENCONTRADO"


class NaoAutorizadoError(AppError):
    status_code = 403
    code = "NAO_AUTORIZADO"


class CredenciaisInvalidasError(AppError):
    status_code = 401
    code = "CREDENCIAIS_INVALIDAS"
