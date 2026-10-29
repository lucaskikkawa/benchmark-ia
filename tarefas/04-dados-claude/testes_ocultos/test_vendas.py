import json
from pathlib import Path

import pytest

from solucao import resumir_vendas

CABECALHO = "data,regiao,produto,quantidade,preco_unitario,status\n"


def escrever(tmp_path, conteudo, nome="vendas.csv"):
    caminho = tmp_path / nome
    caminho.write_text(conteudo, encoding="utf-8")
    return caminho


def rodar(tmp_path, conteudo):
    entrada = escrever(tmp_path, conteudo)
    saida = tmp_path / "saida.json"
    retorno = resumir_vendas(entrada, saida)
    return retorno, json.loads(saida.read_text(encoding="utf-8"))


def test_arquivo_de_exemplo(tmp_path):
    exemplo = Path(__file__).resolve().parent.parent / "vendas_exemplo.csv"
    saida = tmp_path / "s.json"
    retorno = resumir_vendas(str(exemplo), str(saida))
    esperado = {
        "regioes": {
            "Norte": {"quantidade_total": 7, "total_vendas": 8.4, "produto_mais_vendido": "Lápis"},
            "Sul": {"quantidade_total": 12, "total_vendas": 55.0, "produto_mais_vendido": "Caneta"},
        },
        "total_geral": 63.4,
        "linhas_invalidas": 2,
    }
    assert retorno == esperado
    assert json.loads(saida.read_text(encoding="utf-8")) == esperado


def test_retorno_igual_ao_arquivo(tmp_path):
    retorno, gravado = rodar(tmp_path, CABECALHO + "d,Sul,A,1,1.00,concluida\n")
    assert retorno == gravado


def test_json_utf8_sem_escape_e_indent_2(tmp_path):
    entrada = escrever(tmp_path, CABECALHO + "d,São Paulo,Pão,2,1.50,concluida\n")
    saida = tmp_path / "s.json"
    resumir_vendas(entrada, saida)
    texto = saida.read_text(encoding="utf-8")
    assert "São Paulo" in texto and "Pão" in texto
    # indent=2: alguma linha começa com exatamente dois espaços.
    assert any(linha.startswith('  "') and not linha.startswith('   ') for linha in texto.splitlines())


def test_somente_cabecalho(tmp_path):
    retorno, gravado = rodar(tmp_path, CABECALHO)
    assert retorno == {"regioes": {}, "total_geral": 0.0, "linhas_invalidas": 0}
    assert gravado == retorno


def test_status_case_insensitive_e_outros_ignorados(tmp_path):
    conteudo = CABECALHO + (
        "d,Sul,A,1,10.00,CONCLUIDA\n"
        "d,Sul,A,1,10.00, Concluida \n"
        "d,Sul,A,5,10.00,pendente\n"
        "d,Norte,B,5,10.00,cancelada\n"
    )
    retorno, _ = rodar(tmp_path, conteudo)
    assert retorno["regioes"] == {"Sul": {"quantidade_total": 2, "total_vendas": 20.0, "produto_mais_vendido": "A"}}
    assert retorno["linhas_invalidas"] == 0


@pytest.mark.parametrize(
    "linha",
    [
        "d,,A,1,1.00,concluida",
        "d,Sul,,1,1.00,concluida",
        "d,Sul,A,0,1.00,concluida",
        "d,Sul,A,-2,1.00,concluida",
        "d,Sul,A,1.5,1.00,concluida",
        "d,Sul,A,abc,1.00,concluida",
        "d,Sul,A,1,-0.01,concluida",
        'd,Sul,A,1,"2,50",concluida',
        "d,Sul,A,1,,concluida",
    ],
)
def test_linhas_invalidas(tmp_path, linha):
    retorno, _ = rodar(tmp_path, CABECALHO + linha + "\nd,Sul,A,1,1.00,concluida\n")
    assert retorno["linhas_invalidas"] == 1
    assert retorno["regioes"]["Sul"]["quantidade_total"] == 1


def test_invalida_conta_mesmo_se_cancelada(tmp_path):
    retorno, _ = rodar(tmp_path, CABECALHO + "d,Sul,A,x,1.00,cancelada\n")
    assert retorno == {"regioes": {}, "total_geral": 0.0, "linhas_invalidas": 1}


def test_preco_zero_e_espacos(tmp_path):
    retorno, _ = rodar(tmp_path, CABECALHO + " d , Sul , Brinde , 3 , 0 , concluida \n")
    assert retorno["regioes"] == {"Sul": {"quantidade_total": 3, "total_vendas": 0.0, "produto_mais_vendido": "Brinde"}}


def test_regiao_diferencia_maiusculas_e_ordem_alfabetica(tmp_path):
    conteudo = CABECALHO + "d,sul,A,1,1.00,concluida\nd,Sul,A,1,1.00,concluida\nd,Centro,A,1,1.00,concluida\n"
    retorno, _ = rodar(tmp_path, conteudo)
    assert list(retorno["regioes"]) == ["Centro", "Sul", "sul"]


def test_produto_mais_vendido_por_quantidade_e_empate(tmp_path):
    conteudo = CABECALHO + (
        "d,Sul,Caro,1,1000.00,concluida\n"
        "d,Sul,Barato,2,1.00,concluida\n"
        "d,Norte,Zeta,3,1.00,concluida\n"
        "d,Norte,Alfa,1,1.00,concluida\n"
        "d,Norte,Alfa,2,1.00,concluida\n"
    )
    retorno, _ = rodar(tmp_path, conteudo)
    assert retorno["regioes"]["Sul"]["produto_mais_vendido"] == "Barato"
    assert retorno["regioes"]["Norte"]["produto_mais_vendido"] == "Alfa"


def test_arredondamento(tmp_path):
    conteudo = CABECALHO + "d,Sul,A,3,0.10,concluida\nd,Norte,B,1,0.333,concluida\nd,Norte,B,1,0.333,concluida\n"
    retorno, _ = rodar(tmp_path, conteudo)
    assert retorno["regioes"]["Sul"]["total_vendas"] == 0.3
    assert retorno["regioes"]["Norte"]["total_vendas"] == 0.67
    assert retorno["total_geral"] == 0.97


def test_total_geral_soma_totais_ja_arredondados(tmp_path):
    # round(0.001, 2) + round(0.004, 2) = 0; round(0.001 + 0.004, 2) = 0.01.
    conteudo = CABECALHO + "d,A,p,1,0.001,concluida\nd,B,p,1,0.004,concluida\n"
    retorno, _ = rodar(tmp_path, conteudo)
    assert retorno["regioes"]["A"]["total_vendas"] == 0.0
    assert retorno["regioes"]["B"]["total_vendas"] == 0.0
    assert retorno["total_geral"] == 0.0


def test_colunas_em_outra_ordem_e_extras(tmp_path):
    conteudo = "status,preco_unitario,obs,quantidade,produto,regiao,data\nconcluida,2.00,x,4,A,Sul,d\n"
    retorno, _ = rodar(tmp_path, conteudo)
    assert retorno["regioes"]["Sul"] == {"quantidade_total": 4, "total_vendas": 8.0, "produto_mais_vendido": "A"}


def test_coluna_obrigatoria_ausente(tmp_path):
    entrada = escrever(tmp_path, "data,regiao,produto,quantidade,status\nd,Sul,A,1,concluida\n")
    with pytest.raises(ValueError):
        resumir_vendas(entrada, tmp_path / "s.json")


def test_arquivo_inexistente(tmp_path):
    with pytest.raises(FileNotFoundError):
        resumir_vendas(tmp_path / "nao_existe.csv", tmp_path / "s.json")
