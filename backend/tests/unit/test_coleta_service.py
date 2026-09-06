import pytest

from app.services.coleta_service import _calcular_amostras


@pytest.mark.parametrize(
    "quantidade,numerador,denominador,esperado",
    [
        (100, 1, 10, 10),
        (100, 1, 20, 5),
        (8, 1, 10, 1),  # mínimo garantido de 1 amostra
        (1, 1, 1, 1),
        (99, 1, 10, 10),  # arredonda para cima
        (0, 1, 10, 1),  # mesmo com quantidade 0, mínimo 1
    ],
)
def test_calcular_amostras(quantidade, numerador, denominador, esperado):
    assert _calcular_amostras(quantidade, numerador, denominador) == esperado
