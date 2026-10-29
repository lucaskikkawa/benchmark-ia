from pathlib import Path
import random
import subprocess
import sys
import pytest
from pares import contar_pares


def test_inteiros_enormes_e_complementos_vizinhos():
    grande = 10**150
    dados = [grande, -grande, grande + 1, -grande + 1, 0, 0, grande]
    for alvo in (0, 1, 2, grande, -grande, 2 * grande, 2 * grande + 1):
        esperado = sum(a + b == alvo for i, a in enumerate(dados) for b in dados[i+1:])
        assert contar_pares((valor for valor in dados), alvo) == esperado


def test_oraculo_deslocamento_permutacao_e_chamadas_repetidas():
    rng = random.Random(7007)
    for _ in range(60):
        dados = [rng.randrange(-25, 26) for _ in range(60)]
        alvo = rng.randrange(-40, 41)
        esperado = sum(a+b == alvo for i, a in enumerate(dados) for b in dados[i+1:])
        antes = dados[:]
        assert contar_pares(dados, alvo) == esperado and dados == antes
        rng.shuffle(dados)
        deslocamento = 10**90 + rng.randrange(10)
        assert contar_pares((v + deslocamento for v in dados),
                            alvo + 2*deslocamento) == esperado
        assert contar_pares([], alvo) == 0


def test_memoria_do_gerador_depende_de_distintos():
    # Medição em processo separado, sem incluir geração/importação e sem o
    # limite de tempo da prova de velocidade: tracemalloc tem overhead próprio.
    script = '''
import json
import tracemalloc
from pares import contar_pares
n = 1_000_000
dados = (i % 4 for i in range(n))
tracemalloc.start()
resultado = contar_pares(dados, 3)
_, pico = tracemalloc.get_traced_memory()
tracemalloc.stop()
print(json.dumps([resultado, pico]))
'''
    try:
        r = subprocess.run([sys.executable, '-c', script],
                           cwd=Path(__file__).resolve().parents[1],
                           capture_output=True, text=True, timeout=30)
    except subprocess.TimeoutExpired:
        pytest.fail('Medição de memória excedeu 30 segundos')
    assert r.returncode == 0, r.stderr
    import json
    resultado, pico = json.loads(r.stdout.strip().splitlines()[-1])
    assert resultado == 2 * 250_000**2
    assert pico < 4 * 1024**2, f'Pico adicional de {pico} bytes para só quatro valores distintos'
