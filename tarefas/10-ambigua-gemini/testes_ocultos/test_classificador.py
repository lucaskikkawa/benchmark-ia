from pathlib import Path
import pytest
from solucao import classificar_cliente

ROOT_DIR = Path(__file__).resolve().parent.parent


def test_suposicoes_arquivo_existe():
    arquivo_suposicoes = ROOT_DIR / "SUPOSICOES.md"
    assert arquivo_suposicoes.is_file(), (
        "O arquivo SUPOSICOES.md é obrigatório e não foi encontrado na raiz do projeto."
    )


def test_calculo_score_basico():
    cliente = {
        "id": "CLI-001",
        "nome": "João Silva",
        "compras": [100.0, 200.0, 300.0],
        "anos_ativo": 2,
    }
    # 600 * 0.1 = 60.0; 2 * 5 = 10.0; total = 70.0
    res = classificar_cliente(cliente)
    assert res["score"] == 70.0


def test_chaves_obrigatorias_retorno():
    cliente = {
        "id": "CLI-002",
        "nome": "Maria Santos",
        "compras": [50.0],
        "anos_ativo": 1,
    }
    res = classificar_cliente(cliente)
    assert isinstance(res, dict)
    for chave in ["id", "nome", "score", "categoria"]:
        assert chave in res, f"Chave obrigatória '{chave}' ausente no retorno."


def test_categoria_string_nao_vazia():
    cliente = {
        "id": "CLI-003",
        "nome": "Carlos Drummond",
        "compras": [500.0],
        "anos_ativo": 5,
    }
    res = classificar_cliente(cliente)
    assert isinstance(res["categoria"], str)
    assert len(res["categoria"]) > 0


def test_compras_vazias():
    cliente = {
        "id": "CLI-004",
        "nome": "Ana Lima",
        "compras": [],
        "anos_ativo": 3,
    }
    # 0 * 0.1 = 0; 3 * 5 = 15.0
    res = classificar_cliente(cliente)
    assert res["score"] == 15.0


def test_anos_ativo_zero():
    cliente = {
        "id": "CLI-005",
        "nome": "Pedro Alves",
        "compras": [150.0, 250.0],
        "anos_ativo": 0,
    }
    # 400 * 0.1 = 40.0; 0 * 5 = 0; total = 40.0
    res = classificar_cliente(cliente)
    assert res["score"] == 40.0


def test_arredondamento_score():
    cliente = {
        "id": "CLI-006",
        "nome": "Lucia Rocha",
        "compras": [10.33, 20.33],
        "anos_ativo": 1,
    }
    # compras: 30.66 * 0.1 = 3.066; anos: 5; total: 8.066 -> arredonda para 8.07
    res = classificar_cliente(cliente)
    assert res["score"] == 8.07


def test_preservacao_identificadores():
    cliente = {
        "id": "XYZ-999",
        "nome": "Fulano Especial",
        "compras": [10.0],
        "anos_ativo": 1,
    }
    res = classificar_cliente(cliente)
    assert res["id"] == "XYZ-999"
    assert res["nome"] == "Fulano Especial"


def test_independencia_entre_chamadas():
    c1 = {"id": "1", "nome": "A", "compras": [100.0], "anos_ativo": 1}
    c2 = {"id": "2", "nome": "B", "compras": [200.0], "anos_ativo": 2}
    r1 = classificar_cliente(c1)
    r2 = classificar_cliente(c2)
    assert r1["score"] == 15.0
    assert r2["score"] == 30.0


@pytest.mark.parametrize("compras,anos,score", [
    ([], 0, 0.0), ([0, 0.0], 0, 0.0),
    ([10, 20, 30], 1, 11.0), ([0.03, 0.03], 0, 0.01),
    ([1000.0], 10, 150.0),
])
def test_nucleo_com_entradas_nao_negativas(compras, anos, score):
    res = classificar_cliente({"id": "c", "nome": "N", "compras": compras, "anos_ativo": anos})
    assert isinstance(res, dict)
    assert res["id"] == "c"
    assert res["nome"] == "N"
    assert type(res["score"]) in (int, float)
    assert type(res["score"]) is not bool
    assert res["score"] == score
    assert isinstance(res["categoria"], str) and len(res["categoria"]) > 0


def test_nao_modifica_dicionario_de_entrada():
    cliente = {
        "id": "CLI-MUT",
        "nome": "Cliente Imutável",
        "compras": [50.0, 75.0],
        "anos_ativo": 2,
    }
    import copy
    copia_cliente = copy.deepcopy(cliente)
    classificar_cliente(cliente)
    assert cliente == copia_cliente, "A função modificou o dicionário recebido como entrada!"


def test_identificadores_unicode():
    cliente = {
        "id": "ID-★-999/ã",
        "nome": "José François 🚀",
        "compras": [250.0],
        "anos_ativo": 4,
    }
    res = classificar_cliente(cliente)
    assert res["id"] == "ID-★-999/ã"
    assert res["nome"] == "José François 🚀"
    # 250 * 0.1 = 25.0; 4 * 5 = 20.0 -> score = 45.0
    assert res["score"] == 45.0


def test_grande_volume_de_compras():
    # 10.000 compras de 12.34
    compras = [12.34] * 10000
    # soma = 123400.0 -> 10% = 12340.0; anos 10 -> 50.0; total = 12390.0
    cliente = {
        "id": "CLI-BIG",
        "nome": "Cliente Corporativo",
        "compras": compras,
        "anos_ativo": 10,
    }
    res = classificar_cliente(cliente)
    assert res["score"] == 12390.0
