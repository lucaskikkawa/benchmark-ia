import pytest

from solucao import parse_duracao


@pytest.mark.parametrize(
    "entrada, esperado",
    [
        ("45s", 45),
        ("1m", 60),
        ("1h", 3600),
        ("1d", 86400),
        ("1h30m", 5400),
        ("2d 3h 4m 5s", 183845),
        ("2d3h4m5s", 183845),
        ("1d5s", 86405),
    ],
)
def test_componentes_validos(entrada, esperado):
    assert parse_duracao(entrada) == esperado


def test_retorna_int():
    resultado = parse_duracao("1h")
    assert type(resultado) is int


def test_zero():
    assert parse_duracao("0s") == 0
    assert parse_duracao("0h0m") == 0


def test_espacos_nas_bordas_e_entre_componentes():
    assert parse_duracao("  0s  ") == 0
    assert parse_duracao("\t1h   30m\n") == 5400


def test_maiusculas():
    assert parse_duracao("1D1S") == 86401
    assert parse_duracao("1H30m") == 5400


def test_sem_limite_por_componente_e_zeros_a_esquerda():
    assert parse_duracao("90m") == 5400
    assert parse_duracao("007s") == 7
    assert parse_duracao("100000s") == 100000


@pytest.mark.parametrize("entrada", ["", "   ", "\n\t"])
def test_vazio_e_invalido(entrada):
    with pytest.raises(ValueError):
        parse_duracao(entrada)


@pytest.mark.parametrize("entrada", ["90", "1h30", "5x", "h", "1hh", "abc", "1h abc"])
def test_formato_invalido(entrada):
    with pytest.raises(ValueError):
        parse_duracao(entrada)


@pytest.mark.parametrize("entrada", ["-5s", "1.5h", "+3m", "1,5h"])
def test_numeros_negativos_ou_decimais(entrada):
    with pytest.raises(ValueError):
        parse_duracao(entrada)


@pytest.mark.parametrize("entrada", ["30m1h", "5s1d", "1s 1m"])
def test_ordem_errada(entrada):
    with pytest.raises(ValueError):
        parse_duracao(entrada)


@pytest.mark.parametrize("entrada", ["1h2h", "1h 30m 2m", "1s1s"])
def test_unidade_repetida(entrada):
    with pytest.raises(ValueError):
        parse_duracao(entrada)


def test_espaco_entre_numero_e_unidade():
    with pytest.raises(ValueError):
        parse_duracao("1 h")


@pytest.mark.parametrize("entrada", [None, 10, 1.5, b"1h", ["1h"]])
def test_tipo_invalido(entrada):
    with pytest.raises(TypeError):
        parse_duracao(entrada)
