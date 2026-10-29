import csv
import io
import json
import pytest
from vendas import resumir_vendas


def gravar(tmp_path, conteudo, anterior=None):
    entrada, saida = tmp_path / 'ação entrada.csv', tmp_path / 'saída.json'
    entrada.write_text(conteudo, encoding='utf-8', newline='')
    if anterior is not None:
        saida.write_bytes(anterior)
    return entrada, saida


def test_bom_aspas_multilinha_espacos_e_unicode(tmp_path):
    buffer = io.StringIO(newline='')
    escritor = csv.writer(buffer, lineterminator='\r\n')
    escritor.writerow(['extra', 'status', 'preco_centavos', 'produto', 'quantidade'])
    escritor.writerows([
        ['x', ' PAGO\t', ' +0007 ', '  chá, "verde"\nsegunda linha  ', '02'],
        ['x', 'pago', '8', 'chá, "verde"\nsegunda linha', '1'],
        ['x', 'pago', '1', 'é', '1'], ['x', 'pago', '1', 'e\u0301', '1'],
        ['x', 'pago', '-0', '  z\u00a0 z  ', '+0'],
        ['x', 'cancelado', 'não numérico', '', '-999'],
    ])
    entrada, saida = gravar(tmp_path, '\ufeff' + buffer.getvalue(), b'antigo')
    resultado = resumir_vendas(str(entrada), saida)
    esperado = [
        {'produto': 'chá, "verde"\nsegunda linha', 'quantidade': 3, 'receita_centavos': 22},
        {'produto': 'e\u0301', 'quantidade': 1, 'receita_centavos': 1},
        {'produto': 'z\u00a0 z', 'quantidade': 0, 'receita_centavos': 0},
        {'produto': 'é', 'quantidade': 1, 'receita_centavos': 1},
    ]
    assert resultado == esperado
    texto = saida.read_text(encoding='utf-8')
    assert json.loads(texto) == esperado and texto.endswith('\n')
    assert 'chá' in texto and 'é' in texto


@pytest.mark.parametrize('numero', ['1_000', '١٢', '１２', '1e3', '1.0', '+', '--1', '', '-1'])
@pytest.mark.parametrize('campo', ['quantidade', 'preco_centavos'])
def test_gramatica_numerica_e_erro_tardio(tmp_path, numero, campo):
    buffer = io.StringIO()
    escritor = csv.DictWriter(buffer, fieldnames=['produto', 'quantidade', 'preco_centavos', 'status'])
    escritor.writeheader()
    escritor.writerows([dict(produto='antes', quantidade=1, preco_centavos=7, status='pago')] * 100)
    linha = dict(produto='depois', quantidade='1', preco_centavos='1', status='pago')
    linha[campo] = numero
    escritor.writerow(linha)
    anterior = b'\x00\xffconteudo anterior\n'
    entrada, saida = gravar(tmp_path, buffer.getvalue(), anterior)
    with pytest.raises(ValueError):
        resumir_vendas(entrada, saida)
    assert saida.read_bytes() == anterior
    saida.unlink()
    with pytest.raises(ValueError):
        resumir_vendas(entrada, saida)
    assert not saida.exists()


@pytest.mark.parametrize('minimo', [True, False, 0.0, 1.5, '0', None, -10**100])
def test_minimo_invalido_nao_altera_saida(tmp_path, minimo):
    entrada, saida = gravar(tmp_path, 'produto,quantidade,preco_centavos,status\nA,1,2,pago\n', b'original')
    with pytest.raises(ValueError):
        resumir_vendas(entrada, saida, minimo)
    assert saida.read_bytes() == b'original'


def test_colunas_faltantes_apenas_nas_pagas(tmp_path):
    entrada, saida = gravar(tmp_path, 'status,produto,quantidade,preco_centavos\ncancelado\npago,A,1,2\n')
    assert resumir_vendas(entrada, saida) == [dict(produto='A', quantidade=1, receita_centavos=2)]
    entrada.write_text('status,produto,quantidade,preco_centavos\npago,A,1\n', encoding='utf-8')
    antes = saida.read_bytes()
    with pytest.raises(ValueError):
        resumir_vendas(entrada, saida)
    assert saida.read_bytes() == antes


@pytest.mark.parametrize('conteudo', ['', '\ufeff', 'produto,status\n', 'produto,quantidade,preco_centavos\n'])
def test_sem_cabecalho_valido_preserva_saida(tmp_path, conteudo):
    entrada, saida = gravar(tmp_path, conteudo, b'nao apagar')
    with pytest.raises(ValueError):
        resumir_vendas(entrada, saida)
    assert saida.read_bytes() == b'nao apagar'


def test_volume_precisao_filtro_apos_agregacao(tmp_path):
    preco = 10**90 + 13
    linhas = ['produto,quantidade,preco_centavos,status\n']
    linhas.extend(f'P{i % 17:02d},3,{preco},pago\n' for i in range(30_000))
    minimo = 1765 * 3 * preco
    entrada, saida = gravar(tmp_path, ''.join(linhas))
    esperado = [dict(produto=f'P{i:02d}', quantidade=3 * 1765, receita_centavos=minimo)
                for i in range(12)]  # 30.000 = 17 * 1764 + 12
    resultado = resumir_vendas(entrada, str(saida), minimo)
    assert resultado == esperado
    assert json.loads(saida.read_text(encoding='utf-8')) == esperado
