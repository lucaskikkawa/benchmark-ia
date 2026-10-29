import json
from pathlib import Path
import random
import subprocess
import sys

import pytest
from otimizador import maior_subarray_soma


def test_lista_vazia():
    assert maior_subarray_soma([], 0) == 0
    assert maior_subarray_soma([], 10) == 0


def test_alvo_inexistente():
    assert maior_subarray_soma([1, 2, 3, 4], 20) == 0


def test_elemento_unico():
    assert maior_subarray_soma([5], 5) == 1
    assert maior_subarray_soma([5], 3) == 0


def test_exemplo_enunciado():
    assert maior_subarray_soma([1, -1, 5, -2, 3], 3) == 4


def test_negativos_e_positivos():
    assert maior_subarray_soma([-2, -1, 2, 1], 1) == 2


def test_todos_zeros():
    assert maior_subarray_soma([0, 0, 0, 0, 0], 0) == 5


def test_multiplos_subarrays_pega_o_maior():
    assert maior_subarray_soma([3, 1, -1, 1, -1, 1], 3) == 5


def test_lista_inteira_soma_alvo():
    nums = [10, 20, 30, 40]
    assert maior_subarray_soma(nums, 100) == 4


def oraculo_bruto(dados, alvo):
    maior = 0
    for inicio in range(len(dados)):
        soma = 0
        for fim in range(inicio, len(dados)):
            soma += dados[fim]
            if soma == alvo:
                maior = max(maior, fim - inicio + 1)
    return maior


def test_casos_pequenos_contra_oraculo():
    rng = random.Random(2026)
    for _ in range(150):
        dados = [rng.randint(-5, 5) for _ in range(rng.randint(0, 20))]
        alvo = rng.randint(-10, 10)
        assert maior_subarray_soma(dados, alvo) == oraculo_bruto(dados, alvo), (dados, alvo)


def test_alvos_negativos_e_repeticao_de_somas():
    assert maior_subarray_soma([-1, -2, -3], -5) == 2
    assert maior_subarray_soma([2, -2, 2, -2, 2], 0) == 4
    assert maior_subarray_soma([1, 0, 0, 0], 1) == 4


def test_validacao_tipos_entradas():
    with pytest.raises(TypeError):
        maior_subarray_soma([1, 2, "3", 4], 5)
    with pytest.raises(TypeError):
        maior_subarray_soma([1, 2.0, 3], 6)
    with pytest.raises(TypeError):
        maior_subarray_soma([1, True, 3], 4)
    with pytest.raises(TypeError):
        maior_subarray_soma("123", 3)  # type: ignore
    with pytest.raises(TypeError):
        maior_subarray_soma([1, 2, 3], 3.0)  # type: ignore
    with pytest.raises(TypeError):
        maior_subarray_soma([1, 2, 3], True)  # type: ignore


def test_inteiros_gigantes():
    n = 10**30
    dados = [n, -n, n, n, -n]
    assert maior_subarray_soma(dados, n) == 5


@pytest.mark.parametrize("caso", ["alternados", "prefixos_distintos", "aleatorio"])
def test_performance_entrada_grande(caso, tmp_path):
    tamanho = 350_000
    if caso == "alternados":
        dados, alvo, esperado = [1, -1] * (tamanho // 2), 1, tamanho - 1
    elif caso == "prefixos_distintos":
        dados, alvo, esperado = [1] * tamanho, 12_345, 12_345
    else:
        rng = random.Random(42)
        dados, alvo = [rng.randint(-5, 5) for _ in range(tamanho)], 42
        primeiras, ultimas = {0: 0}, {0: 0}
        soma = 0
        for posicao, valor in enumerate(dados, 1):
            soma += valor
            primeiras.setdefault(soma, posicao)
            ultimas[soma] = posicao
        esperado = max([0] + [
            ultimas[soma + alvo] - posicao
            for soma, posicao in primeiras.items() if soma + alvo in ultimas
        ])

    programa = """
import json
import sys
import time
from otimizador import maior_subarray_soma
dados, alvo = json.load(sys.stdin)
inicio = time.perf_counter()
resultado = maior_subarray_soma(dados, alvo)
duracao = time.perf_counter() - inicio
with open(sys.argv[1], "w", encoding="utf-8") as arquivo:
    json.dump([resultado, duracao], arquivo)
"""
    metricas = tmp_path / "metricas.json"
    try:
        execucao = subprocess.run(
            [sys.executable, "-c", programa, str(metricas)],
            cwd=Path(__file__).resolve().parent.parent,
            input=json.dumps([dados, alvo]), capture_output=True, text=True, timeout=15,
        )
    except subprocess.TimeoutExpired:
        pytest.fail("A execução excedeu 15s, incluindo a inicialização do processo.")
    assert execucao.returncode == 0, execucao.stdout + execucao.stderr
    resultado, duracao = json.loads(metricas.read_text(encoding="utf-8"))
    assert type(resultado) is int
    assert resultado == esperado
    assert duracao < 5.0, f"Algoritmo muito lento: levou {duracao:.3f}s (limite: 5s)"
