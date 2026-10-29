import json
from pathlib import Path
import random
import subprocess
import sys
import pytest
from pares import contar_pares


def test_vazio():
    assert contar_pares([], 0) == 0


def test_unitario_nao_pareia_consigo():
    assert contar_pares([2], 4) == 0


def test_exemplo():
    assert contar_pares([1, 3, 2, 2], 4) == 2


def test_duplicatas():
    assert contar_pares([2, 2, 2, 2], 4) == 6


def test_negativos():
    assert contar_pares([-3, -1, 0, 1, 3, 3], 0) == 3


def test_zeros():
    assert contar_pares([0, 0, 0], 0) == 3


def test_sem_pares():
    assert contar_pares([1, 3, 7], 99) == 0


def test_gerador_e_nao_mutacao():
    dados = [4, -1, 4, -1]
    assert contar_pares(iter(dados), 3) == 4
    assert contar_pares(dados, 3) == 4
    assert dados == [4, -1, 4, -1]


def test_oraculo_pequeno_deterministico():
    rng = random.Random(452)
    for _ in range(40):
        dados = [rng.randrange(-10, 11) for _ in range(rng.randrange(25))]
        alvo = rng.randrange(-20, 21)
        esperado = sum(dados[i] + dados[j] == alvo for i in range(len(dados)) for j in range(i + 1, len(dados)))
        assert contar_pares(dados, alvo) == esperado


@pytest.mark.parametrize('modo,n,alvo,esperado', [
    ('distintos', 200_000, 199_999, 100_000),
    ('repetidos', 150_000, 0, 150_000 * 149_999 // 2),
])
def test_limite_de_tempo(modo, n, alvo, esperado):
    script = """
import json
import sys
from time import perf_counter
from pares import contar_pares
modo, n, alvo = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
dados = list(range(n)) if modo == 'distintos' else [0] * n
inicio = perf_counter()
resultado = contar_pares(dados, alvo)
duracao = perf_counter() - inicio
print(json.dumps([resultado, duracao]))
"""
    try:
        r = subprocess.run([sys.executable, '-c', script, modo, str(n), str(alvo)],
                           cwd=Path(__file__).resolve().parents[1], capture_output=True,
                           text=True, timeout=5)
    except subprocess.TimeoutExpired:
        pytest.fail('Algoritmo excedeu o limite externo de 5 segundos')
    assert r.returncode == 0, r.stderr
    # Usa a última linha: prints acidentais da solução não devem quebrar a medição.
    resultado, duracao = json.loads(r.stdout.strip().splitlines()[-1])
    assert resultado == esperado
    assert duracao < 2.0, f'Chamada levou {duracao:.3f}s, limite 2s'
