from pydantic import BaseModel, ConfigDict

from app.models.peca import StatusCadastro


class TipoInstrumentoBase(BaseModel):
    nome: str
    descricao_funcao: str | None = None


class TipoInstrumentoCreate(TipoInstrumentoBase):
    pass


class TipoInstrumentoUpdate(BaseModel):
    nome: str | None = None
    descricao_funcao: str | None = None
    status: StatusCadastro | None = None


class TipoInstrumentoRead(TipoInstrumentoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: StatusCadastro
    tem_imagem: bool
