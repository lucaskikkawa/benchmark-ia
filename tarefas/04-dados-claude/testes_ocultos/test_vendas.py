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


def test_linhas_invalidas(tmp_path):
    for linha in [
        "d,,A,1,1.00,concluida",
        "d,Sul,,1,1.00,concluida",
        "d,Sul,A,0,1.00,concluida",
        "d,Sul,A,-2,1.00,concluida",
        "d,Sul,A,1.5,1.00,concluida",
        "d,Sul,A,abc,1.00,concluida",
        "d,Sul,A,1,-0.01,concluida",
        'd,Sul,A,1,"2,50",concluida',
        "d,Sul,A,1,,concluida",
    ]:
        retorno, _ = rodar(tmp_path, CABECALHO + linha + "\nd,Sul,A,1,1.00,concluida\n")
        assert retorno["linhas_invalidas"] == 1, linha
        assert retorno["regioes"]["Sul"]["quantidade_total"] == 1, linha


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


# ---- requisitos adicionais ----

def test_bom_utf8(tmp_path):
    entrada = tmp_path / "bom.csv"
    entrada.write_bytes(("﻿" + CABECALHO + "d,Sul,A,2,1.50,concluida\n").encode("utf-8"))
    retorno = resumir_vendas(entrada, tmp_path / "s.json")
    assert retorno["regioes"] == {"Sul": {"quantidade_total": 2, "total_vendas": 3.0, "produto_mais_vendido": "A"}}


def test_cabecalho_com_espacos_e_crlf(tmp_path):
    entrada = tmp_path / "crlf.csv"
    conteudo = " data , regiao ,produto, quantidade ,preco_unitario , status \r\nd,Sul,A,2,1.00,concluida\r\n"
    entrada.write_bytes(conteudo.encode("utf-8"))
    retorno = resumir_vendas(entrada, tmp_path / "s.json")
    assert retorno["regioes"]["Sul"]["quantidade_total"] == 2
    assert retorno["linhas_invalidas"] == 0


def test_nome_de_coluna_diferencia_maiusculas(tmp_path):
    entrada = escrever(tmp_path, "data,Regiao,produto,quantidade,preco_unitario,status\nd,Sul,A,1,1.00,concluida\n")
    with pytest.raises(ValueError):
        resumir_vendas(entrada, tmp_path / "s.json")


def test_campos_entre_aspas_com_virgula_e_quebra_de_linha(tmp_path):
    conteudo = CABECALHO + (
        'd,Sul,"Caneta, azul",3,1.00,concluida\n'
        'd,"Norte\nLeste","Caderno ""A4""",2,5.00,concluida\n'
        'd,Sul,"Caneta, azul",1,1.00,concluida\n'
    )
    retorno, _ = rodar(tmp_path, conteudo)
    assert retorno["regioes"] == {
        "Norte\nLeste": {"quantidade_total": 2, "total_vendas": 10.0, "produto_mais_vendido": 'Caderno "A4"'},
        "Sul": {"quantidade_total": 4, "total_vendas": 4.0, "produto_mais_vendido": "Caneta, azul"},
    }
    assert retorno["linhas_invalidas"] == 0


def test_numero_de_campos_diferente_do_cabecalho(tmp_path):
    conteudo = CABECALHO + (
        "d,Sul,A,1,1.00\n"                      # campo a menos
        "d,Sul,A,1,1.00,concluida,extra\n"      # campo a mais
        "d,Sul,A,1,1.00,concluida\n"
    )
    retorno, _ = rodar(tmp_path, conteudo)
    assert retorno["linhas_invalidas"] == 2
    assert retorno["regioes"]["Sul"]["quantidade_total"] == 1


def test_linhas_vazias_ignoradas(tmp_path):
    conteudo = CABECALHO + "\nd,Sul,A,1,1.00,concluida\n\n\nd,Sul,A,1,1.00,concluida\n\n"
    retorno, _ = rodar(tmp_path, conteudo)
    assert retorno["linhas_invalidas"] == 0
    assert retorno["regioes"]["Sul"]["quantidade_total"] == 2


def test_preco_nao_finito_e_invalido(tmp_path):
    for preco in ["nan", "inf", "-inf", "Infinity", "NaN"]:
        retorno, gravado = rodar(tmp_path, CABECALHO + f"d,Sul,A,1,{preco},concluida\nd,Sul,A,1,1.00,concluida\n")
        assert retorno["linhas_invalidas"] == 1, preco
        assert retorno["regioes"]["Sul"]["total_vendas"] == 1.0, preco
        assert gravado == retorno


def test_conversao_igual_a_int_e_float(tmp_path):
    conteudo = CABECALHO + (
        "d,Sul,A,+3,1e2,concluida\n"
        "d,Sul,B,007,.5,concluida\n"
        "d,Sul,C,4,  2.  ,concluida\n"
    )
    retorno, _ = rodar(tmp_path, conteudo)
    assert retorno["linhas_invalidas"] == 0
    assert retorno["regioes"]["Sul"] == {"quantidade_total": 14, "total_vendas": 311.5, "produto_mais_vendido": "B"}


def test_concluida_com_acento_nao_conta(tmp_path):
    conteudo = CABECALHO + "d,Sul,A,1,1.00,concluída\nd,Sul,A,2,1.00,CONCLUIDA\n"
    retorno, _ = rodar(tmp_path, conteudo)
    assert retorno["linhas_invalidas"] == 0
    assert retorno["regioes"]["Sul"]["quantidade_total"] == 2


def test_empate_por_comparacao_simples_de_str(tmp_path):
    conteudo = CABECALHO + (
        "d,Sul,Água,2,1.00,concluida\n"
        "d,Sul,Zebra,2,1.00,concluida\n"
        "d,Sul,abacaxi,2,1.00,concluida\n"
        "d,Norte,banana,1,1.00,concluida\n"
        "d,Norte,Banana,1,1.00,concluida\n"
    )
    retorno, _ = rodar(tmp_path, conteudo)
    assert retorno["regioes"]["Sul"]["produto_mais_vendido"] == "Zebra"
    assert retorno["regioes"]["Norte"]["produto_mais_vendido"] == "Banana"


def test_regioes_em_ordem_de_str(tmp_path):
    conteudo = CABECALHO + "".join(f"d,{r},A,1,1.00,concluida\n" for r in ["Ébano", "sul", "Sul", "Acre", "árvore"])
    retorno, gravado = rodar(tmp_path, conteudo)
    assert list(retorno["regioes"]) == ["Acre", "Sul", "sul", "Ébano", "árvore"]
    assert list(gravado["regioes"]) == ["Acre", "Sul", "sul", "Ébano", "árvore"]


def test_tipos_dos_valores_no_json(tmp_path):
    entrada = escrever(tmp_path, CABECALHO + "d,Sul,Brinde,3,0,concluida\n")
    saida = tmp_path / "s.json"
    retorno = resumir_vendas(entrada, saida)
    texto = saida.read_text(encoding="utf-8")
    assert type(retorno["regioes"]["Sul"]["total_vendas"]) is float
    assert type(retorno["total_geral"]) is float
    assert type(retorno["regioes"]["Sul"]["quantidade_total"]) is int
    gravado = json.loads(texto)
    assert type(gravado["regioes"]["Sul"]["total_vendas"]) is float
    assert type(gravado["total_geral"]) is float


def test_somente_cabecalho_total_float(tmp_path):
    entrada = escrever(tmp_path, CABECALHO)
    saida = tmp_path / "s.json"
    retorno = resumir_vendas(entrada, saida)
    assert type(retorno["total_geral"]) is float
    assert type(json.loads(saida.read_text(encoding="utf-8"))["total_geral"]) is float


def test_cria_diretorios_pais_da_saida(tmp_path):
    entrada = escrever(tmp_path, CABECALHO + "d,Sul,A,1,1.00,concluida\n")
    saida = tmp_path / "a" / "b" / "resumo.json"
    retorno = resumir_vendas(str(entrada), str(saida))
    assert json.loads(saida.read_text(encoding="utf-8")) == retorno


def test_arquivo_vazio_sem_cabecalho(tmp_path):
    entrada = escrever(tmp_path, "")
    saida = tmp_path / "s.json"
    with pytest.raises(ValueError):
        resumir_vendas(entrada, saida)
    assert not saida.exists()


def test_erro_nao_cria_nem_altera_saida(tmp_path):
    entrada = escrever(tmp_path, "data,regiao,produto,quantidade,status\nd,Sul,A,1,concluida\n")
    saida = tmp_path / "s.json"
    with pytest.raises(ValueError):
        resumir_vendas(entrada, saida)
    assert not saida.exists()
    saida.write_text("ANTIGO", encoding="utf-8")
    with pytest.raises(ValueError):
        resumir_vendas(entrada, saida)
    with pytest.raises(FileNotFoundError):
        resumir_vendas(tmp_path / "nao_existe.csv", saida)
    assert saida.read_text(encoding="utf-8") == "ANTIGO"


def test_arquivo_grande(tmp_path):
    linhas = [CABECALHO]
    for i in range(100_000):
        regiao = f"R{i % 7}"
        produto = f"P{i % 13}"
        linhas.append(f"2024-01-01,{regiao},{produto},{i % 5 + 1},{(i % 10) / 4},concluida\n")
    linhas.append("d,R0,X,0,1.00,concluida\n")
    retorno, gravado = rodar(tmp_path, "".join(linhas))
    assert retorno == gravado
    assert retorno["linhas_invalidas"] == 1
    assert sum(r["quantidade_total"] for r in retorno["regioes"].values()) == sum(i % 5 + 1 for i in range(100_000))
    esperado_r0 = round(sum((i % 5 + 1) * ((i % 10) / 4) for i in range(0, 100_000, 7)), 2)
    assert retorno["regioes"]["R0"]["total_vendas"] == pytest.approx(esperado_r0, abs=0.011)
