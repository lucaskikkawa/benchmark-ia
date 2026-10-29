from pathlib import Path
import random
import subprocess
import sys
import pytest
from janelas import somas_janelas


def test_oraculo_todos_tamanhos():
    rng = random.Random(3112)
    for n in range(36):
        dados = [rng.randrange(-10**25, 10**25) for _ in range(n)]
        antes = dados[:]
        for tamanho in range(1, n + 3):
            esperado = [sum(dados[i:i+tamanho]) for i in range(n-tamanho+1)]
            assert somas_janelas(dados, tamanho) == esperado
            assert dados == antes


@pytest.mark.parametrize('tamanho', [1, 2, 3, 4, 7])
def test_cancelamento_com_inteiros_enormes(tamanho):
    grande = 10**180
    dados = [grande, 1, -grande, grande + 7, -grande - 3, 0, -5]
    resultado = somas_janelas(dados, tamanho)
    assert resultado == [sum(dados[i:i+tamanho]) for i in range(8-tamanho)]
    assert all(type(valor) is int for valor in resultado)


def test_invalidos_com_lista_nao_vazia_e_tamanho_enorme():
    dados = [9, -3, 1]
    for tamanho in (0, -1, -10**80):
        with pytest.raises(ValueError):
            somas_janelas(dados, tamanho)
        assert dados == [9, -3, 1]
    assert somas_janelas(dados, 10**100) == []


def test_resultados_nao_compartilhados():
    dados = [1, 2, 3]
    primeiro = somas_janelas(dados, 1)
    primeiro[0] = 999
    assert dados == [1, 2, 3]
    assert somas_janelas(dados, 1) == [1, 2, 3]
    assert somas_janelas(dados, 2) == [3, 5]
    assert primeiro == [999, 2, 3]


def test_janela_grande_varredura_linear():
    # 10 bilhões de elementos somados por uma solução com cortes repetidos.
    # O limite externo é folgado para a varredura O(n), sem cronometragem apertada.
    script = '''
from janelas import somas_janelas
n, tamanho = 200_000, 100_000
dados = list(range(n))
resultado = somas_janelas(dados, tamanho)
assert resultado == [tamanho * (2*i + tamanho - 1) // 2
                     for i in range(n-tamanho+1)]
assert dados == list(range(n))
'''
    try:
        r = subprocess.run([sys.executable, '-c', script],
                           cwd=Path(__file__).resolve().parents[1],
                           capture_output=True, text=True, timeout=15)
    except subprocess.TimeoutExpired:
        pytest.fail('A varredura O(n) deve processar 200.000 valores em até 15s')
    assert r.returncode == 0, r.stdout + r.stderr
