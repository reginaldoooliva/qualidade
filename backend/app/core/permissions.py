import enum


class Perfil(str, enum.Enum):
    GESTOR_QUALIDADE = "gestor_qualidade"
    ANALISTA_QUALIDADE = "analista_qualidade"
    INSPETOR = "inspetor"
    OPERADOR = "operador"


# Perfis com acesso de "Qualidade/Admin" — cadastros, reabertura de rodadas, tratamento de RNC/CAPA.
PERFIS_QUALIDADE = (Perfil.ANALISTA_QUALIDADE, Perfil.GESTOR_QUALIDADE)

# Somente o Gestor administra usuários e acessa relatórios consolidados.
PERFIS_GESTAO = (Perfil.GESTOR_QUALIDADE,)
