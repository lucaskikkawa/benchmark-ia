import json
import pytest
from vendas import resumir_vendas

CAB = 'produto,quantidade,preco_centavos,status\n'


def executar(tmp_path, linhas, minimo=0, cab=CAB):
    entrada, saida = tmp_path / 'entrada.csv', tmp_path / 'saida.json'
    entrada.write_text(cab + linhas, encoding='utf-8')
    resultado = resumir_vendas(entrada, saida, minimo)
    assert json.loads(saida.read_text(encoding='utf-8')) == resultado
    assert saida.read_bytes().endswith(b'\n')
    return resultado


def test_agrega_e_ordena(tmp_path):
    assert executar(tmp_path, 'B,2,50,pago\nA,1,40,pago\nB,3,20,pago\n') == [
        {'produto': 'A', 'quantidade': 1, 'receita_centavos': 40},
        {'produto': 'B', 'quantidade': 5, 'receita_centavos': 160}]


def test_filtra_depois_de_agregar_e_inclui_limite(tmp_path):
    assert executar(tmp_path, 'A,1,30,pago\nA,1,30,pago\nB,1,59,pago\n', 60) == [
        {'produto': 'A', 'quantidade': 2, 'receita_centavos': 60}]


def test_ignora_cancelado_invalido(tmp_path):
    assert executar(tmp_path, ',lixo,-5,cancelado\nA,1,2,pago\n') == [
        {'produto': 'A', 'quantidade': 1, 'receita_centavos': 2}]


def test_normalizacao_e_acentos(tmp_path):
    resultado = executar(tmp_path, ' café ,2,3, PAGO \ncafé,1,3,pago\n')
    assert resultado == [{'produto': 'café', 'quantidade': 3, 'receita_centavos': 9}]
    assert 'café' in (tmp_path / 'saida.json').read_text(encoding='utf-8')


def test_aspas_e_reordenacao(tmp_path):
    assert executar(tmp_path, 'pago,7,"chá, verde",2,x\n', cab='status,preco_centavos,produto,quantidade,extra\n') == [
        {'produto': 'chá, verde', 'quantidade': 2, 'receita_centavos': 14}]


def test_vazio(tmp_path):
    assert executar(tmp_path, '') == []


def test_zero_e_caixa_distinta(tmp_path):
    assert executar(tmp_path, 'A,0,4,pago\na,1,0,pago\n') == [
        {'produto': 'A', 'quantidade': 0, 'receita_centavos': 0},
        {'produto': 'a', 'quantidade': 1, 'receita_centavos': 0}]


@pytest.mark.parametrize('linha', ['A,-1,2,pago', 'A,1,-2,pago', 'A,x,2,pago',
                                  'A,1,2.5,pago', ' ,1,2,pago', 'A,1,,pago'])
def test_linha_invalida_preserva_saida(tmp_path, linha):
    entrada, saida = tmp_path / 'i.csv', tmp_path / 's.json'
    entrada.write_text(CAB + 'B,1,2,pago\n' + linha + '\n', encoding='utf-8')
    saida.write_text('anterior', encoding='utf-8')
    with pytest.raises(ValueError):
        resumir_vendas(str(entrada), str(saida))
    assert saida.read_text(encoding='utf-8') == 'anterior'


def test_cabecalho_incompleto(tmp_path):
    entrada, saida = tmp_path / 'i.csv', tmp_path / 's.json'
    entrada.write_text('produto,quantidade,status\nA,1,pago\n', encoding='utf-8')
    with pytest.raises(ValueError):
        resumir_vendas(entrada, saida)
    assert not saida.exists()


def test_minimo_negativo(tmp_path):
    entrada, saida = tmp_path / 'i.csv', tmp_path / 's.json'
    entrada.write_text(CAB, encoding='utf-8')
    with pytest.raises(ValueError):
        resumir_vendas(entrada, saida, -1)
    assert not saida.exists()
