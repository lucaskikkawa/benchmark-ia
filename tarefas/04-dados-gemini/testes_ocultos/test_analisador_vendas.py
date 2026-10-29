import json
import pytest
from analisador_vendas import processar_vendas


@pytest.fixture
def csv_basico(tmp_path):
    arquivo = tmp_path / "vendas.csv"
    arquivo.write_text(
        "id_transacao,data,cliente,categoria,valor,status\n"
        "1,2026-01-01,Alice,Livros,50.00,concluido\n"
        "2,2026-01-02,Bob,Eletronicos,120.50,concluido\n"
        "3,2026-01-03,Alice,Livros,30.00,concluido\n"
        "4,2026-01-04,Carlos,Roupas,70.00,cancelado\n"
        "5,2026-01-05,Bob,Livros,15.25,concluido\n",
        encoding="utf-8",
    )
    return arquivo


def test_processamento_basico(csv_basico, tmp_path):
    saida = tmp_path / "resultado.json"
    res = processar_vendas(str(csv_basico), str(saida), status_filtro="concluido", top_n=2)

    assert res["total_transacoes"] == 4
    assert res["receita_total"] == 215.75
    assert res["ticket_medio"] == 53.94
    assert res["por_categoria"] == {
        "Eletronicos": 120.50,
        "Livros": 95.25,
    }
    assert res["top_clientes"] == [
        {"cliente": "Bob", "total": 135.75},
        {"cliente": "Alice", "total": 80.0},
    ]

    assert saida.is_file()
    dados_salvos = json.loads(saida.read_text(encoding="utf-8"))
    assert dados_salvos == res


def test_filtro_status_case_insensitive(csv_basico, tmp_path):
    saida = tmp_path / "resultado_cancelados.json"
    res = processar_vendas(str(csv_basico), str(saida), status_filtro="CANCELADO")
    assert res["total_transacoes"] == 1
    assert res["receita_total"] == 70.0
    assert res["top_clientes"] == [{"cliente": "Carlos", "total": 70.0}]


def test_csv_apenas_cabecalho(tmp_path):
    arquivo = tmp_path / "vazio.csv"
    arquivo.write_text("id_transacao,data,cliente,categoria,valor,status\n", encoding="utf-8")
    saida = tmp_path / "saida_vazio.json"

    res = processar_vendas(str(arquivo), str(saida))
    assert res["total_transacoes"] == 0
    assert res["receita_total"] == 0.0
    assert res["ticket_medio"] == 0.0
    assert res["por_categoria"] == {}
    assert res["top_clientes"] == []


def test_csv_totalmente_vazio_zero_bytes(tmp_path):
    arquivo = tmp_path / "zero_bytes.csv"
    arquivo.write_bytes(b"")
    saida = tmp_path / "saida_zero.json"

    res = processar_vendas(str(arquivo), str(saida))
    assert res["total_transacoes"] == 0
    assert res["receita_total"] == 0.0
    assert res["ticket_medio"] == 0.0
    assert res["por_categoria"] == {}
    assert res["top_clientes"] == []
    assert saida.is_file()


def test_linhas_com_valores_invalidos(tmp_path):
    arquivo = tmp_path / "invalidos.csv"
    arquivo.write_text(
        "id_transacao,data,cliente,categoria,valor,status\n"
        "1,2026-01-01,Alice,Livros,invalido,concluido\n"
        "2,2026-01-02,Bob,Eletronicos,-50.00,concluido\n"
        "3,2026-01-03,Carlos,Roupas,40.00,concluido\n",
        encoding="utf-8",
    )
    saida = tmp_path / "saida_inv.json"
    res = processar_vendas(str(arquivo), str(saida))
    assert res["total_transacoes"] == 1
    assert res["receita_total"] == 40.0
    assert res["top_clientes"] == [{"cliente": "Carlos", "total": 40.0}]


def test_desempate_alfabetico_top_clientes(tmp_path):
    arquivo = tmp_path / "empate.csv"
    arquivo.write_text(
        "id_transacao,data,cliente,categoria,valor,status\n"
        "1,2026-01-01,Zelia,A,100.0,concluido\n"
        "2,2026-01-02,Arthur,B,100.0,concluido\n"
        "3,2026-01-03,Bruno,C,100.0,concluido\n",
        encoding="utf-8",
    )
    saida = tmp_path / "saida_empate.json"
    res = processar_vendas(str(arquivo), str(saida), top_n=3)
    assert res["top_clientes"] == [
        {"cliente": "Arthur", "total": 100.0},
        {"cliente": "Bruno", "total": 100.0},
        {"cliente": "Zelia", "total": 100.0},
    ]


def test_top_n_maior_que_clientes_existentes(csv_basico, tmp_path):
    saida = tmp_path / "saida_top_grande.json"
    res = processar_vendas(str(csv_basico), str(saida), top_n=50)
    assert len(res["top_clientes"]) == 2


def test_arquivo_inexistente(tmp_path):
    with pytest.raises(FileNotFoundError):
        processar_vendas(str(tmp_path / "nao_existe.csv"), str(tmp_path / "saida.json"))


def test_top_n_invalido_valor(csv_basico, tmp_path):
    with pytest.raises(ValueError):
        processar_vendas(str(csv_basico), str(tmp_path / "saida.json"), top_n=0)
    with pytest.raises(ValueError):
        processar_vendas(str(csv_basico), str(tmp_path / "saida.json"), top_n=-3)


def test_top_n_invalido_tipo(csv_basico, tmp_path):
    with pytest.raises(TypeError):
        processar_vendas(str(csv_basico), str(tmp_path / "saida.json"), top_n=True)  # type: ignore
    with pytest.raises(TypeError):
        processar_vendas(str(csv_basico), str(tmp_path / "saida.json"), top_n=2.5)  # type: ignore


def test_diretorio_nao_e_arquivo_csv(tmp_path):
    with pytest.raises(FileNotFoundError):
        processar_vendas(str(tmp_path), str(tmp_path / "saida.json"))


def test_status_normaliza_linha_e_filtro(tmp_path):
    entrada = tmp_path / "status.csv"
    entrada.write_text(
        "id_transacao,data,cliente,categoria,valor,status\n"
        "1,2026-01-01,A,Livros,10, CoNcLuIdO  \n"
        "2,2026-01-01,B,Livros,30,cancelado\n",
        encoding="utf-8",
    )
    res = processar_vendas(str(entrada), str(tmp_path / "saida.json"), " CONCLUIDO ")
    assert res["total_transacoes"] == 1
    assert res["receita_total"] == 10.0
    assert res["top_clientes"] == [{"cliente": "A", "total": 10.0}]


def test_nenhuma_linha_corresponde_ao_filtro(csv_basico, tmp_path):
    res = processar_vendas(str(csv_basico), str(tmp_path / "saida.json"), "pendente")
    assert res == {
        "total_transacoes": 0, "receita_total": 0.0, "ticket_medio": 0.0,
        "por_categoria": {}, "top_clientes": [],
    }


def test_zero_valor_vazio_ordem_categorias_e_top_um(tmp_path):
    entrada = tmp_path / "bordas.csv"
    entrada.write_text(
        "id_transacao,data,cliente,categoria,valor,status\n"
        "1,2026-01-01,Zoe,Z,0,concluido\n"
        "2,2026-01-01,Ana,A,10,concluido\n"
        "3,2026-01-01,Bia,B,,concluido\n",
        encoding="utf-8",
    )
    res = processar_vendas(str(entrada), str(tmp_path / "saida.json"), top_n=1)
    assert res["total_transacoes"] == 2
    assert res["receita_total"] == 10.0
    assert res["ticket_medio"] == 5.0
    assert res["por_categoria"] == {"A": 10.0, "Z": 0.0}
    assert list(res["por_categoria"]) == ["A", "Z"]
    assert res["top_clientes"] == [{"cliente": "Ana", "total": 10.0}]


def test_cria_subdiretorios_de_saida_automaticamente(csv_basico, tmp_path):
    saida_profunda = tmp_path / "profundo" / "nivel2" / "nivel3" / "resultado.json"
    res = processar_vendas(str(csv_basico), str(saida_profunda))
    assert saida_profunda.is_file()
    assert json.loads(saida_profunda.read_text(encoding="utf-8")) == res


def test_bom_utf8_e_espacos_nas_colunas(tmp_path):
    entrada = tmp_path / "bom.csv"
    conteudo = (
        "\ufeff id_transacao , data , cliente , categoria , valor , status \n"
        "1,2026-01-01,  Maria Clara  ,  Roupas & Acessórios  ,  150.25  ,  concluido  \n"
    )
    entrada.write_text(conteudo, encoding="utf-8")
    saida = tmp_path / "saida_bom.json"
    res = processar_vendas(str(entrada), str(saida))
    assert res["total_transacoes"] == 1
    assert res["receita_total"] == 150.25
    assert res["por_categoria"] == {"Roupas & Acessórios": 150.25}
    assert res["top_clientes"] == [{"cliente": "Maria Clara", "total": 150.25}]


def test_dataset_grande(tmp_path):
    linhas = ["id_transacao,data,cliente,categoria,valor,status"]
    for i in range(1, 1001):
        cliente = f"Cliente_{i % 50}"
        cat = f"Cat_{i % 5}"
        valor = f"{10.0 + (i % 100) * 0.5:.2f}"
        linhas.append(f"{i},2026-01-01,{cliente},{cat},{valor},concluido")

    arquivo = tmp_path / "grande.csv"
    arquivo.write_text("\n".join(linhas), encoding="utf-8")
    saida = tmp_path / "saida_grande.json"
    res = processar_vendas(str(arquivo), str(saida), top_n=5)
    assert res["total_transacoes"] == 1000
    assert len(res["por_categoria"]) == 5
    assert len(res["top_clientes"]) == 5
