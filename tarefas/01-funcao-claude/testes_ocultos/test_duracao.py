import json
import subprocess
import sys
from pathlib import Path

import pytest

from solucao import parse_duracao

DIR_TRABALHO = Path(__file__).resolve().parent.parent


def test_componentes_validos():
    casos = [
        ("45s", 45),
        ("1m", 60),
        ("1h", 3600),
        ("1d", 86400),
        ("1h30m", 5400),
        ("2d 3h 4m 5s", 183845),
        ("2d3h4m5s", 183845),
        ("1d5s", 86405),
    ]
    for entrada, esperado in casos:
        assert parse_duracao(entrada) == esperado, entrada


def test_unidade_semana():
    assert parse_duracao("1w") == 604800
    assert parse_duracao("1w 1s") == 604801
    assert parse_duracao("1w2d3h4m5s") == 604800 + 2 * 86400 + 3 * 3600 + 4 * 60 + 5
    assert parse_duracao("2W") == 1209600


def test_retorna_int():
    resultado = parse_duracao("1h")
    assert type(resultado) is int


def test_zero():
    assert parse_duracao("0s") == 0
    assert parse_duracao("0h0m") == 0
    assert parse_duracao("0w0d0h0m0s") == 0


def test_espacos_nas_bordas_e_entre_componentes():
    assert parse_duracao("  0s  ") == 0
    assert parse_duracao("\t1h   30m\n") == 5400
    assert parse_duracao("1w\n\n2d\r\n3s") == 604800 + 2 * 86400 + 3


def test_maiusculas():
    assert parse_duracao("1D1S") == 86401
    assert parse_duracao("1H30m") == 5400
    assert parse_duracao("1W1d") == 691200


def test_sem_limite_por_componente_e_zeros_a_esquerda():
    assert parse_duracao("90m") == 5400
    assert parse_duracao("007s") == 7
    assert parse_duracao("100000s") == 100000
    assert parse_duracao("123456789012345678901234567890s") == 123456789012345678901234567890


def test_milhares_de_digitos_resultado_exato():
    assert parse_duracao("9" * 10_000 + "s") == 10**10_000 - 1
    assert parse_duracao("1" + "0" * 5_000 + "m") == 60 * 10**5_000


def test_milhares_de_zeros_a_esquerda():
    assert parse_duracao("0" * 6_000 + "7s") == 7
    assert parse_duracao("1w " + "2" * 4_500 + "s") == 604800 + int("2" * 1_500) * (10**3_000 + 10**1_500 + 1)


def test_vazio_e_invalido():
    for entrada in ["", "   ", "\n\t"]:
        with pytest.raises(ValueError):
            parse_duracao(entrada)


def test_formato_invalido():
    for entrada in ["90", "1h30", "5x", "h", "1hh", "abc", "1h abc", "1h,30m", "1h+30m", "1ms", "s5", "1h 30m x"]:
        with pytest.raises(ValueError):
            parse_duracao(entrada)


def test_digitos_nao_ascii_sao_invalidos():
    entradas = [
        "\u0661h",        # dígito arábico-índico 1
        "\uff11h",        # dígito de largura total 1
        "\u00b2s",        # sobrescrito 2
        "1\u0661s",
        "\u09e7d",        # dígito bengali 1
    ]
    for entrada in entradas:
        with pytest.raises(ValueError):
            parse_duracao(entrada)


@pytest.mark.parametrize(
    "entrada",
    [
        "5\u017f",        # "ſ" (s longo): casefold/upper/IGNORECASE o tratam como "s"
        "3\u212a",        # sinal de Kelvin (IGNORECASE o trata como "k")
        "1\uff48",        # "ｈ" de largura total
    ],
    ids=["s_longo", "kelvin", "h_largura_total"],
)
def test_unidades_unicode_parecidas_sao_invalidas(entrada):
    with pytest.raises(ValueError):
        parse_duracao(entrada)


def test_numeros_negativos_ou_decimais():
    for entrada in ["-5s", "1.5h", "+3m", "1,5h", "1_000s", "1e3s"]:
        with pytest.raises(ValueError):
            parse_duracao(entrada)


def test_ordem_errada():
    for entrada in ["30m1h", "5s1d", "1s 1m", "1d1w", "1h 2w"]:
        with pytest.raises(ValueError):
            parse_duracao(entrada)


def test_unidade_repetida():
    for entrada in ["1h2h", "1h 30m 2m", "1s1s", "1w1W", "1h1H"]:
        with pytest.raises(ValueError):
            parse_duracao(entrada)


def test_espaco_entre_numero_e_unidade():
    for entrada in ["1 h", "1h 30 m", "1\th"]:
        with pytest.raises(ValueError):
            parse_duracao(entrada)


def test_tipo_invalido():
    for entrada in [None, 10, 1.5, b"1h", ["1h"], bytearray(b"1h")]:
        with pytest.raises(TypeError):
            parse_duracao(entrada)


def test_bool_e_tipo_invalido():
    with pytest.raises(TypeError):
        parse_duracao(True)


def test_subclasse_de_str_e_aceita():
    class Texto(str):
        pass

    assert parse_duracao(Texto("1h 1s")) == 3601


# A medição roda em subprocesso: uma solução com backtracking exponencial/polinomial
# é morta pelo timeout em vez de travar a suíte. O tempo medido é só o das chamadas.
SCRIPT_TEMPO = r"""
import json, sys, time
sys.path.insert(0, sys.argv[1])
from solucao import parse_duracao
n = 500_000
casos = {
    "invalido_no_fim": ("1d" + " " * n + "x", None),
    "invalido_meio": ("1w " + " " * n + "1d" + " " * n + "1h 1h", None),
    "valido_espacado": (" " * n + "1h" + " " * n + "30m" + "\t" * n, 5400),
    "so_espacos": (" " * (2 * n), None),
    "digitos_e_espacos": ("1" + " " * n + "1", None),
}
saida = {}
for nome, (texto, esperado) in casos.items():
    inicio = time.perf_counter()
    try:
        obtido = parse_duracao(texto)
    except ValueError:
        obtido = None
    saida[nome] = {"ok": obtido == esperado, "tempo": time.perf_counter() - inicio}
print(json.dumps(saida))
"""


def test_desempenho_linear_em_entradas_grandes():
    try:
        r = subprocess.run(
            [sys.executable, "-c", SCRIPT_TEMPO, str(DIR_TRABALHO)],
            capture_output=True, text=True, timeout=20,
        )
    except subprocess.TimeoutExpired:
        pytest.fail("entradas grandes não terminaram em 20 s (tempo não linear)")
    assert r.returncode == 0, r.stderr[-2000:]
    saida = json.loads(r.stdout.strip().splitlines()[-1])
    for nome, medida in saida.items():
        assert medida["ok"], f"resultado errado no caso {nome}"
        assert medida["tempo"] < 1.0, f"caso {nome}: {medida['tempo']:.2f}s"
