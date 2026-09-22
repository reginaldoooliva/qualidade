from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env.local", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str
    jwt_secret: str = "dev-secret-nao-usar-em-producao"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 600
    cors_origins: list[str] = ["http://localhost:5173"]

    # Cp/Cpk: abaixo deste nº de amostras, exibe aviso de baixa robustez estatística (não bloqueia).
    cpk_limiar_baixa_robustez: int = 20
    # Classificação: Cpk < limiar_nao_capaz -> não capaz; até limiar_capaz -> atenção; acima -> capaz.
    cpk_limiar_nao_capaz: float = 1.00
    cpk_limiar_capaz: float = 1.33


@lru_cache
def get_settings() -> Settings:
    return Settings()
