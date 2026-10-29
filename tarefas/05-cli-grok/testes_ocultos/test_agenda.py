import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
SCRIPT = RAIZ / "agenda_cli.py"


def _run(*args, timeout=5):
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    try:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=env,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        pytest.fail(f"Comando excedeu o limite de {timeout}s: {args}")


def _erro(proc, mensagem):
    assert proc.returncode == 2
    assert proc.stdout == ""
    assert proc.stderr == f"erro: {mensagem}\n"


def test_adicionar_cria_arquivo_e_ids(tmp_path):
    arquivo = tmp_path / "agenda.json"
    primeiro = _run(
        "adicionar",
        "--titulo",
        "  Comprar leite  ",
        "--prioridade",
        "alta",
        "--arquivo",
        str(arquivo),
    )
    assert primeiro.returncode == 0
    assert primeiro.stdout == "ok id=1\n"
    assert primeiro.stderr == ""
    segundo = _run(
        "adicionar",
        "--titulo",
        "café",
        "--prioridade",
        "baixa",
        "--prazo",
        "2024-02-29",
        "--arquivo",
        str(arquivo),
    )
    assert segundo.stdout == "ok id=2\n"
    dados = json.loads(arquivo.read_text(encoding="utf-8"))
    assert dados["proximo_id"] == 3
    assert dados["tarefas"][0]["titulo"] == "Comprar leite"
    assert dados["tarefas"][0]["prazo"] is None
    assert dados["tarefas"][0]["concluida"] is False
    assert dados["tarefas"][1]["titulo"] == "café"
    assert dados["tarefas"][1]["prazo"] == "2024-02-29"
    assert arquivo.read_text(encoding="utf-8").endswith("\n")
    assert "café" in arquivo.read_text(encoding="utf-8")


def test_listar_ordem_prazo_e_estado(tmp_path):
    arquivo = tmp_path / "agenda.json"
    arquivo.write_text(
        json.dumps(
            {
                "proximo_id": 5,
                "tarefas": [
                    {
                        "id": 1,
                        "titulo": "Pagar",
                        "prioridade": "baixa",
                        "prazo": "2024-05-01",
                        "concluida": False,
                    },
                    {
                        "id": 2,
                        "titulo": "Comprar",
                        "prioridade": "alta",
                        "prazo": None,
                        "concluida": False,
                    },
                    {
                        "id": 4,
                        "titulo": "Feito",
                        "prioridade": "alta",
                        "prazo": None,
                        "concluida": True,
                    },
                    {
                        "id": 3,
                        "titulo": "Revisar",
                        "prioridade": "media",
                        "prazo": "2024-06-01",
                        "concluida": False,
                    },
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    proc = _run("listar", "--arquivo", str(arquivo))
    assert proc.returncode == 0
    assert proc.stderr == ""
    assert proc.stdout == (
        "2\talta\taberta\t-\tComprar\n"
        "4\talta\tconcluida\t-\tFeito\n"
        "3\tmedia\taberta\t2024-06-01\tRevisar\n"
        "1\tbaixa\taberta\t2024-05-01\tPagar\n"
    )


def test_filtros_e_lista_vazia(tmp_path):
    arquivo = tmp_path / "agenda.json"
    _run(
        "adicionar",
        "--titulo",
        "Uma",
        "--prioridade",
        "alta",
        "--arquivo",
        str(arquivo),
    )
    _run(
        "adicionar",
        "--titulo",
        "Duas",
        "--prioridade",
        "baixa",
        "--arquivo",
        str(arquivo),
    )
    _run("concluir", "--id", "1", "--arquivo", str(arquivo))
    abertas = _run("listar", "--arquivo", str(arquivo), "--somente-abertas")
    assert abertas.stdout == "2\tbaixa\taberta\t-\tDuas\n"
    alta_aberta = _run(
        "listar",
        "--arquivo",
        str(arquivo),
        "--prioridade",
        "alta",
        "--somente-abertas",
    )
    assert alta_aberta.returncode == 0
    assert alta_aberta.stdout == ""
    assert alta_aberta.stderr == ""
    vazio = tmp_path / "vazio.json"
    _run(
        "adicionar",
        "--titulo",
        "temp",
        "--prioridade",
        "media",
        "--arquivo",
        str(vazio),
    )
    dados = json.loads(vazio.read_text(encoding="utf-8"))
    dados["tarefas"] = []
    dados["proximo_id"] = 2
    vazio.write_text(json.dumps(dados), encoding="utf-8")
    lista = _run("listar", "--arquivo", str(vazio))
    assert lista.returncode == 0
    assert lista.stdout == ""


def test_concluir_sucesso_e_erros(tmp_path):
    arquivo = tmp_path / "agenda.json"
    _run(
        "adicionar",
        "--titulo",
        "Tarefa",
        "--prioridade",
        "media",
        "--arquivo",
        str(arquivo),
    )
    ok = _run("concluir", "--id", "1", "--arquivo", str(arquivo))
    assert ok.returncode == 0
    assert ok.stdout == "ok id=1\n"
    assert ok.stderr == ""
    assert json.loads(arquivo.read_text(encoding="utf-8"))["tarefas"][0]["concluida"] is True
    de_novo = _run("concluir", "--id", "1", "--arquivo", str(arquivo))
    _erro(de_novo, "ja concluida")
    inexistente = _run("concluir", "--id", "9", "--arquivo", str(arquivo))
    _erro(inexistente, "id inexistente")
    negativo = _run("concluir", "--id", "0", "--arquivo", str(arquivo))
    _erro(negativo, "id inexistente")


def test_titulo_vazio_e_invalido(tmp_path):
    arquivo = tmp_path / "agenda.json"
    vazio = _run(
        "adicionar",
        "--titulo",
        "   ",
        "--prioridade",
        "baixa",
        "--arquivo",
        str(arquivo),
    )
    _erro(vazio, "titulo vazio")
    assert not arquivo.exists()
    tab = _run(
        "adicionar",
        "--titulo",
        "a\tb",
        "--prioridade",
        "baixa",
        "--arquivo",
        str(arquivo),
    )
    _erro(tab, "titulo invalido")
    quebra = _run(
        "adicionar",
        "--titulo",
        "a\nb",
        "--prioridade",
        "alta",
        "--arquivo",
        str(arquivo),
    )
    _erro(quebra, "titulo invalido")


def test_prazo_invalido(tmp_path):
    arquivo = tmp_path / "agenda.json"
    for prazo in ("2023-02-29", "2024-13-01", "2024-1-01", "01/02/2024", "20240229"):
        proc = _run(
            "adicionar",
            "--titulo",
            "X",
            "--prioridade",
            "media",
            "--prazo",
            prazo,
            "--arquivo",
            str(arquivo),
        )
        _erro(proc, "prazo invalido")
    assert not arquivo.exists()


def test_arquivo_inexistente(tmp_path):
    arquivo = tmp_path / "nao.json"
    _erro(_run("listar", "--arquivo", str(arquivo)), "arquivo inexistente")
    _erro(
        _run("concluir", "--id", "1", "--arquivo", str(arquivo)),
        "arquivo inexistente",
    )


def test_arquivo_invalido(tmp_path):
    arquivo = tmp_path / "ruim.json"
    for texto in ("{", "[]", '{"proximo_id": 1, "tarefas": [{"id": 5}]}', "123"):
        arquivo.write_text(texto, encoding="utf-8")
        _erro(_run("listar", "--arquivo", str(arquivo)), "arquivo invalido")


def test_proximo_id_nao_pode_colidir(tmp_path):
    arquivo = tmp_path / "agenda.json"
    arquivo.write_text(
        json.dumps(
            {
                "proximo_id": 1,
                "tarefas": [
                    {
                        "id": 1,
                        "titulo": "Velha",
                        "prioridade": "baixa",
                        "prazo": None,
                        "concluida": False,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    _erro(_run("listar", "--arquivo", str(arquivo)), "arquivo invalido")


def test_uso_argparse(tmp_path):
    arquivo = tmp_path / "agenda.json"
    sem_comando = _run()
    assert sem_comando.returncode == 2
    falta_titulo = _run("adicionar", "--prioridade", "alta", "--arquivo", str(arquivo))
    assert falta_titulo.returncode == 2
    prioridade = _run(
        "adicionar",
        "--titulo",
        "X",
        "--prioridade",
        "urgente",
        "--arquivo",
        str(arquivo),
    )
    assert prioridade.returncode == 2
    id_ruim = _run("concluir", "--id", "1.5", "--arquivo", str(arquivo))
    assert id_ruim.returncode == 2
    assert not arquivo.exists()


def _tarefa(identificador, titulo="T", prioridade="baixa", prazo=None, concluida=False):
    return {
        "id": identificador,
        "titulo": titulo,
        "prioridade": prioridade,
        "prazo": prazo,
        "concluida": concluida,
    }


def test_buraco_de_id_nao_renumera(tmp_path):
    arquivo = tmp_path / "agenda.json"
    arquivo.write_text(
        json.dumps(
            {"proximo_id": 5, "tarefas": [_tarefa(1, "Um"), _tarefa(3, "Três")]},
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    antes = arquivo.read_bytes()
    lista = _run("listar", "--arquivo", str(arquivo))
    assert lista.returncode == 0
    assert lista.stdout == "1\tbaixa\taberta\t-\tUm\n3\tbaixa\taberta\t-\tTrês\n"
    assert arquivo.read_bytes() == antes
    novo = _run(
        "adicionar",
        "--arquivo",
        str(arquivo),
        "--prioridade",
        "alta",
        "--titulo",
        "Nova",
    )
    assert novo.returncode == 0
    assert novo.stdout == "ok id=5\n"
    dados = json.loads(arquivo.read_text(encoding="utf-8"))
    assert dados["proximo_id"] == 6
    assert [item["id"] for item in dados["tarefas"]] == [1, 3, 5]


def test_arquivo_invalido_nao_e_reescrito(tmp_path):
    arquivo = tmp_path / "agenda.json"
    arquivo.write_text("{", encoding="utf-8")
    proc = _run(
        "adicionar",
        "--titulo",
        "X",
        "--prioridade",
        "baixa",
        "--arquivo",
        str(arquivo),
    )
    _erro(proc, "arquivo invalido")
    assert arquivo.read_text(encoding="utf-8") == "{"


def test_strip_unicode_e_datas_gregorianas(tmp_path):
    arquivo = tmp_path / "agenda.json"
    vazio = _run(
        "adicionar",
        "--titulo",
        "\u00a0\u00a0",
        "--prioridade",
        "baixa",
        "--arquivo",
        str(arquivo),
    )
    _erro(vazio, "titulo vazio")
    assert not arquivo.exists()
    for prazo in ("1900-02-29", "2100-02-29", "0000-01-01"):
        proc = _run(
            "adicionar",
            "--titulo",
            "X",
            "--prioridade",
            "alta",
            "--prazo",
            prazo,
            "--arquivo",
            str(arquivo),
        )
        _erro(proc, "prazo invalido")
    ok = _run(
        "adicionar",
        "--titulo",
        "\u00a0café\u00a0",
        "--prioridade",
        "media",
        "--prazo",
        "2000-02-29",
        "--arquivo",
        str(arquivo),
    )
    assert ok.returncode == 0
    assert ok.stdout == "ok id=1\n"
    dados = json.loads(arquivo.read_text(encoding="utf-8"))
    assert dados["tarefas"][0]["titulo"] == "café"
    assert dados["tarefas"][0]["prazo"] == "2000-02-29"
    natal = _run(
        "adicionar",
        "--titulo",
        "Ano um",
        "--prioridade",
        "baixa",
        "--prazo",
        "0001-12-25",
        "--arquivo",
        str(arquivo),
    )
    assert natal.returncode == 0
    assert natal.stdout == "ok id=2\n"


def test_formas_invalidas_do_json(tmp_path):
    arquivo = tmp_path / "agenda.json"
    base = {"proximo_id": 3, "tarefas": [_tarefa(1), _tarefa(2, "Outra")]}
    variantes = []
    extra = json.loads(json.dumps(base))
    extra["tarefas"][0]["nota"] = 1
    variantes.append(extra)
    duplicado = json.loads(json.dumps(base))
    duplicado["tarefas"][1]["id"] = 1
    duplicado["proximo_id"] = 2
    variantes.append(duplicado)
    flag = json.loads(json.dumps(base))
    flag["tarefas"][0]["concluida"] = 1
    variantes.append(flag)
    flutuante = json.loads(json.dumps(base))
    flutuante["proximo_id"] = 3.0
    variantes.append(flutuante)
    booleano = json.loads(json.dumps(base))
    booleano["proximo_id"] = True
    variantes.append(booleano)
    titulo = json.loads(json.dumps(base))
    titulo["tarefas"][0]["titulo"] = "  a"
    variantes.append(titulo)
    for dados in variantes:
        arquivo.write_text(json.dumps(dados), encoding="utf-8")
        _erro(_run("listar", "--arquivo", str(arquivo)), "arquivo invalido")


def test_concluir_id_com_zero_a_esquerda(tmp_path):
    arquivo = tmp_path / "agenda.json"
    _run("adicionar", "--titulo", "Uma", "--prioridade", "alta", "--arquivo", str(arquivo))
    ok = _run("concluir", "--id", "01", "--arquivo", str(arquivo))
    assert ok.returncode == 0
    assert ok.stdout == "ok id=1\n"
    assert json.loads(arquivo.read_text(encoding="utf-8"))["tarefas"][0]["concluida"] is True
