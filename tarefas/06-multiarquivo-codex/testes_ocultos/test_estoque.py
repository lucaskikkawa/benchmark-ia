from dataclasses import FrozenInstanceError, is_dataclass
import json
from pathlib import Path
import pytest
import estoque
from estoque import Movimento, calcular_saldos, carregar_movimentos


def test_exportacoes_e_quatro_modulos():
    assert estoque.Movimento is Movimento
    assert callable(estoque.calcular_saldos) and callable(estoque.carregar_movimentos)
    pasta = Path(estoque.__file__).parent
    assert {p.name for p in pasta.glob('*.py')} == {
        '__init__.py', 'modelos.py', 'operacoes.py', 'persistencia.py'}


def test_modelo_dataclass_imutavel():
    m = Movimento('A', 2)
    assert is_dataclass(m) and m == Movimento('A', 2)
    with pytest.raises(FrozenInstanceError):
        m.delta = 3


def test_vazio():
    assert calcular_saldos([]) == {}


def test_iniciais_copiados_e_retidos():
    iniciais = {'A': 4, 'B': 0}
    resultado = calcular_saldos([], iniciais)
    assert resultado == iniciais and resultado is not iniciais
    assert calcular_saldos([Movimento('A', -2)], iniciais) == {'A': 2, 'B': 0}
    assert iniciais == {'A': 4, 'B': 0}


def test_gerador_e_novo_sku():
    dados = (m for m in [Movimento('ç', 3), Movimento('ç', -3), Movimento('B', 0)])
    assert calcular_saldos(dados) == {'ç': 0, 'B': 0}


def test_ordem_nao_compensa_negativo():
    with pytest.raises(ValueError):
        calcular_saldos([Movimento('A', -1), Movimento('A', 4)])


def test_inicial_negativo():
    with pytest.raises(ValueError):
        calcular_saldos([], {'A': -1})


def test_varios_skus():
    assert calcular_saldos([Movimento('A', 2), Movimento('B', 8), Movimento('A', -1)], {'A': 1}) == {'A': 2, 'B': 8}


def test_carregar_e_integrar(tmp_path):
    p = tmp_path / 'movimentos.json'
    p.write_text(json.dumps([{'sku': 'ação', 'delta': 3, 'extra': 9},
                             {'sku': 'ação', 'delta': -1}, {'sku': ' X ', 'delta': 0}]), encoding='utf-8')
    dados = carregar_movimentos(str(p))
    assert dados == [Movimento('ação', 3), Movimento('ação', -1), Movimento(' X ', 0)]
    assert calcular_saldos(dados) == {'ação': 2, ' X ': 0}


def test_json_vazio(tmp_path):
    p = tmp_path / 'vazio.json'
    p.write_text('[]', encoding='utf-8')
    assert carregar_movimentos(p) == []


@pytest.mark.parametrize('dados', [{}, None, [1], [{'sku': 'A'}], [{'delta': 1}],
    [{'sku': '', 'delta': 1}], [{'sku': '  ', 'delta': 1}], [{'sku': 2, 'delta': 1}],
    [{'sku': 'A', 'delta': True}], [{'sku': 'A', 'delta': 1.0}], [{'sku': 'A', 'delta': '1'}]])
def test_json_estrutura_invalida(tmp_path, dados):
    p = tmp_path / 'invalido.json'
    p.write_text(json.dumps(dados), encoding='utf-8')
    with pytest.raises(ValueError):
        carregar_movimentos(p)


def test_json_malformado(tmp_path):
    p = tmp_path / 'quebrado.json'
    p.write_text('[', encoding='utf-8')
    with pytest.raises(ValueError):
        carregar_movimentos(p)
