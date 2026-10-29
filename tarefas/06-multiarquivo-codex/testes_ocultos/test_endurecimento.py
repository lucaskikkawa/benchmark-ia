from dataclasses import FrozenInstanceError
import json
import pytest
from estoque import Movimento, calcular_saldos, carregar_movimentos
from estoque.modelos import Movimento as Modelo
from estoque.operacoes import calcular_saldos as Operacao
from estoque.persistencia import carregar_movimentos as Carregador


def test_api_dos_modulos_e_construtor_sem_validacao():
    assert Movimento is Modelo and calcular_saldos is Operacao
    assert carregar_movimentos is Carregador
    # A validação está no carregador, não no dataclass.
    m = Movimento('', True)
    assert m.sku == '' and m.delta is True
    assert Movimento('A', 1) != Movimento('a', 1)
    assert Movimento('A', 1) != Movimento('A', 2)
    with pytest.raises(FrozenInstanceError):
        m.sku = 'outro'


def test_iniciais_preservados_apos_falha_tardia():
    iniciais = {'A': 5, 'intocado': 0}
    movimentos = [Movimento('A', -2), Movimento('novo', 7),
                  Movimento('A', -4), Movimento('A', 100)]
    with pytest.raises(ValueError):
        calcular_saldos(iter(movimentos), iniciais)
    assert iniciais == {'A': 5, 'intocado': 0}
    assert movimentos == [Movimento('A', -2), Movimento('novo', 7),
                           Movimento('A', -4), Movimento('A', 100)]
    assert calcular_saldos(iter(()), iniciais) == iniciais


def test_saldo_negativo_inicial_nao_pode_ser_reposto():
    with pytest.raises(ValueError):
        calcular_saldos(iter([Movimento('A', 10)]), {'A': -1})


def test_saldos_enormes_precisao_skus_exatos_e_sem_estado():
    grande = 10**150
    iniciais = {'A': grande, 'a': 0, ' A ': 1, 'é': 2, 'e\u0301': 3}
    resultado = calcular_saldos((m for m in [
        Movimento('A', -grande + 1), Movimento('A', -1),
        Movimento('a', grande + 7), Movimento('a', -grande),
        Movimento('🧪', 0)]), iniciais)
    assert resultado == {'A': 0, 'a': 7, ' A ': 1, 'é': 2, 'e\u0301': 3, '🧪': 0}
    assert iniciais['A'] == grande and '🧪' not in iniciais
    resultado['a'] = -99
    assert calcular_saldos([]) == {}
    assert calcular_saldos([], iniciais) == iniciais
    with pytest.raises(ValueError):
        calcular_saldos([Movimento('A', -grande - 1)], iniciais)
    assert iniciais['A'] == grande


@pytest.mark.parametrize('invalido', [
    False, 0, '', [[]], [None], [True],
    [{'sku': None, 'delta': 0}], [{'sku': False, 'delta': 0}],
    [{'sku': '\u2003\u00a0\t\n', 'delta': 0}],
    [{'sku': 'A', 'delta': False}], [{'sku': 'A', 'delta': None}],
    [{'sku': 'A', 'delta': []}], [{'sku': 'A', 'delta': {}}],
    [{'sku': 'A', 'delta': -1.0}],
])
def test_json_invalido_e_chamada_posterior_valida(tmp_path, invalido):
    p = tmp_path / 'dados.json'
    p.write_text(json.dumps(invalido), encoding='utf-8')
    with pytest.raises(ValueError):
        carregar_movimentos(p)
    p.write_text('[{"sku":"A","delta":0}]', encoding='utf-8')
    assert carregar_movimentos(p) == [Movimento('A', 0)]


def test_integracao_volume_arquivo_recarregado(tmp_path):
    skus = [' A ', 'a', 'é', 'e\u0301', '🧪']
    grande = 10**80 + 1
    objetos = [dict(sku=skus[(i // 2) % 5], delta=grande if i % 2 == 0 else -grande,
                    ignorar={'delta': True}) for i in range(20_000)]
    p = tmp_path / 'ação.json'
    p.write_text(json.dumps(objetos, ensure_ascii=False), encoding='utf-8')
    movimentos = carregar_movimentos(p)
    assert movimentos == [Movimento(item['sku'], item['delta']) for item in objetos]
    assert calcular_saldos(iter(movimentos)) == dict.fromkeys(skus, 0)
    movimentos.clear()
    assert len(carregar_movimentos(str(p))) == 20_000


def test_json_erro_no_ultimo_item(tmp_path):
    p = tmp_path / 'fim.json'
    dados = [{'sku': 'A', 'delta': 1}] * 300 + [{'sku': 'A', 'delta': True}]
    p.write_text(json.dumps(dados), encoding='utf-8')
    with pytest.raises(ValueError):
        carregar_movimentos(p)
