import pytest

from app.services.capabilidade_service import calcular_estatisticas, classificar_cpk


def test_sem_amostras():
    resultado = calcular_estatisticas([], lie=5, lse=15)
    assert resultado["n_amostras"] == 0
    assert resultado["media"] is None
    assert resultado["cp"] is None
    assert resultado["cpk"] is None
    assert resultado["baixa_robustez"] is False


def test_uma_amostra_nao_calcula_desvio():
    resultado = calcular_estatisticas([10.0], lie=5, lse=15)
    assert resultado["n_amostras"] == 1
    assert resultado["media"] == 10.0
    assert resultado["desvio_padrao"] is None
    assert resultado["cp"] is None
    assert resultado["cpk"] is None
    assert resultado["baixa_robustez"] is True


def test_processo_centrado_capaz():
    # média=10, desvio amostral (n-1)=1, LIE=5, LSE=15
    resultado = calcular_estatisticas([9.0, 10.0, 11.0], lie=5, lse=15)
    assert resultado["n_amostras"] == 3
    assert resultado["media"] == pytest.approx(10.0)
    assert resultado["desvio_padrao"] == pytest.approx(1.0)
    assert resultado["cp"] == pytest.approx(10 / 6)
    assert resultado["cpk"] == pytest.approx(10 / 6)
    assert resultado["classificacao"] == "capaz"
    assert resultado["baixa_robustez"] is True  # n < 20


def test_processo_descentrado_nao_capaz():
    # média=10, desvio=1, LIE=8, LSE=15 -> Cpk limitado pelo lado inferior
    resultado = calcular_estatisticas([9.0, 10.0, 11.0], lie=8, lse=15)
    assert resultado["cp"] == pytest.approx(7 / 6)
    assert resultado["cpk"] == pytest.approx(2 / 3)
    assert resultado["classificacao"] == "nao_capaz"


def test_processo_atencao():
    # Cpk = 1.1 -> classificação "atencao" (1.00-1.33)
    # LIE=5, LSE=15, média=10, desvio=1.5152 -> cpk = min(5/(3*1.515), 5/(3*1.515)) ~ 1.1
    valores = [8.5, 10.0, 11.5]  # desvio amostral = 1.5, cpk = 5/4.5 = 1.111
    resultado = calcular_estatisticas(valores, lie=5, lse=15)
    assert resultado["classificacao"] == "atencao"


def test_baixa_robustez_acima_do_limiar():
    valores = [10.0] * 25
    resultado = calcular_estatisticas(valores, lie=5, lse=15)
    assert resultado["baixa_robustez"] is False


def test_desvio_zero_nao_calcula_cpk():
    resultado = calcular_estatisticas([10.0, 10.0, 10.0], lie=5, lse=15)
    assert resultado["desvio_padrao"] == 0.0
    assert resultado["cp"] is None
    assert resultado["cpk"] is None
    assert resultado["classificacao"] is None


@pytest.mark.parametrize(
    "cpk,esperado",
    [
        (0.5, "nao_capaz"),
        (0.99, "nao_capaz"),
        (1.00, "atencao"),
        (1.20, "atencao"),
        (1.33, "atencao"),
        (1.34, "capaz"),
        (2.0, "capaz"),
    ],
)
def test_classificar_cpk(cpk, esperado):
    assert classificar_cpk(cpk) == esperado
