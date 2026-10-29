import json

import pytest

from solucao import consolidar

SLA = {"limites_minutos": {"baixa": 480, "media": 240, "alta": 60}}
CABECALHO = "id,equipe,aberto_em,fechado_em,prioridade\n"


def _gravar(tmp_path, csv_texto, sla=None):
    csv_path = tmp_path / "chamados.csv"
    sla_path = tmp_path / "sla.json"
    saida = tmp_path / "resumo.json"
    csv_path.write_text(csv_texto, encoding="utf-8")
    sla_path.write_text(
        json.dumps(SLA if sla is None else sla, ensure_ascii=False),
        encoding="utf-8",
    )
    return str(csv_path), str(sla_path), str(saida)


def _rodar(tmp_path, csv_texto, sla=None):
    caminhos = _gravar(tmp_path, csv_texto, sla)
    retorno = consolidar(*caminhos)
    texto = (tmp_path / "resumo.json").read_text(encoding="utf-8")
    assert texto.endswith("\n")
    assert json.loads(texto) == retorno
    return retorno, texto


def test_exemplo_de_estouro_estrito_e_media_piso(tmp_path):
    csv_texto = (
        CABECALHO
        + "a1,n1,2024-03-01T10:00,2024-03-01T11:01,alta\n"
        + "b2,n1,2024-03-01T10:00,2024-03-01T10:30,alta\n"
    )
    retorno, _ = _rodar(tmp_path, csv_texto)
    assert retorno == {
        "equipes": [
            {
                "equipe": "n1",
                "chamados": 2,
                "estourados": 1,
                "tempo_medio_minutos": 45,
                "pior_id": "a1",
            }
        ]
    }


def test_limite_exato_nao_estoura_e_duracao_zero(tmp_path):
    csv_texto = (
        CABECALHO
        + "z,sup,2024-01-01T00:00,2024-01-01T01:00,alta\n"
        + "a,sup,2024-01-01T08:00,2024-01-01T08:00,baixa\n"
    )
    retorno, _ = _rodar(tmp_path, csv_texto)
    assert retorno["equipes"] == [
        {
            "equipe": "sup",
            "chamados": 2,
            "estourados": 0,
            "tempo_medio_minutos": 30,
            "pior_id": "z",
        }
    ]


def test_empate_de_duracao_escolhe_menor_id(tmp_path):
    csv_texto = (
        CABECALHO
        + "m,eq,2024-05-01T10:00,2024-05-01T12:00,media\n"
        + "a,eq,2024-05-01T10:00,2024-05-01T12:00,media\n"
        + "b,eq,2024-05-01T10:00,2024-05-01T10:01,baixa\n"
    )
    retorno, _ = _rodar(tmp_path, csv_texto)
    equipe = retorno["equipes"][0]
    assert equipe["pior_id"] == "a"
    assert equipe["chamados"] == 3
    assert equipe["estourados"] == 0
    assert equipe["tempo_medio_minutos"] == (120 + 120 + 1) // 3


def test_varias_equipes_ordenadas_e_unicode(tmp_path):
    csv_texto = (
        CABECALHO
        + "1,beta,2024-06-01T09:00,2024-06-01T09:10,baixa\n"
        + "2,São Paulo,2024-06-01T09:00,2024-06-01T13:01,media\n"
        + "3,alfa,2024-06-01T09:00,2024-06-01T09:05,baixa\n"
    )
    retorno, texto = _rodar(tmp_path, csv_texto)
    assert [item["equipe"] for item in retorno["equipes"]] == [
        "São Paulo",
        "alfa",
        "beta",
    ]
    assert "São Paulo" in texto
    assert "\\u" not in texto
    sao = retorno["equipes"][0]
    assert sao["estourados"] == 1
    assert sao["tempo_medio_minutos"] == 241
    assert sao["pior_id"] == "2"


def test_strip_id_preserva_zeros_e_ignora_linha_em_branco(tmp_path):
    csv_texto = (
        CABECALHO
        + "\n"
        + "  007 , n1 , 2024-07-01T10:00 , 2024-07-01T10:02 , baixa \n"
        + "\n"
    )
    retorno, _ = _rodar(tmp_path, csv_texto)
    assert retorno["equipes"][0]["pior_id"] == "007"
    assert retorno["equipes"][0]["tempo_medio_minutos"] == 2
    assert retorno["equipes"][0]["estourados"] == 0


def test_csv_so_com_cabecalho(tmp_path):
    retorno, _ = _rodar(tmp_path, CABECALHO + "\n   \n")
    assert retorno == {"equipes": []}


def test_sobrescreve_saida(tmp_path):
    csv_texto = CABECALHO + "1,a,2024-01-02T00:00,2024-01-02T00:03,baixa\n"
    csv_path, sla_path, saida = _gravar(tmp_path, csv_texto)
    (tmp_path / "resumo.json").write_text("lixo", encoding="utf-8")
    retorno = consolidar(csv_path, sla_path, saida)
    assert retorno["equipes"][0]["tempo_medio_minutos"] == 3
    assert json.loads((tmp_path / "resumo.json").read_text(encoding="utf-8")) == retorno


def test_ordem_das_linhas_nao_importa(tmp_path):
    base = [
        "b,z,2024-08-01T00:00,2024-08-01T02:00,alta",
        "a,z,2024-08-01T00:00,2024-08-01T00:10,alta",
    ]
    ida, _ = _rodar(tmp_path, CABECALHO + "\n".join(base) + "\n")
    volta, _ = _rodar(tmp_path, CABECALHO + "\n".join(reversed(base)) + "\n")
    assert ida == volta
    assert ida["equipes"][0]["estourados"] == 1
    assert ida["equipes"][0]["pior_id"] == "b"


def test_arquivo_ausente(tmp_path):
    with pytest.raises(FileNotFoundError):
        consolidar(
            str(tmp_path / "nao.csv"),
            str(tmp_path / "nao.json"),
            str(tmp_path / "out.json"),
        )


def test_cabecalho_e_colunas_invalidos(tmp_path):
    with pytest.raises(ValueError):
        _rodar(tmp_path, "id,equipe,aberto_em,fechado_em\n")
    with pytest.raises(ValueError):
        _rodar(
            tmp_path,
            CABECALHO + "1,eq,2024-01-01T00:00,2024-01-01T00:01,baixa,extra\n",
        )


def test_datas_prioridade_duplicata_e_vazio(tmp_path):
    ruins = [
        "1,eq,2024-02-30T00:00,2024-03-01T00:00,baixa\n",
        "1,eq,2024-01-01T10:00,2024-01-01T09:00,baixa\n",
        "1,eq,2024-01-01 10:00,2024-01-01T11:00,baixa\n",
        "1,eq,2024-01-01T10:00,2024-01-01T11:00,Alta\n",
        "1,eq,2024-01-01T10:00,2024-01-01T11:00,urgente\n",
        "1,,2024-01-01T10:00,2024-01-01T11:00,baixa\n",
        ",eq,2024-01-01T10:00,2024-01-01T11:00,baixa\n",
        "1,eq,2024-01-01T10:00,2024-01-01T11:00,baixa\n"
        "1,eq,2024-01-02T10:00,2024-01-02T11:00,baixa\n",
        "1,eq,2024-01-01T10:00,2024-01-02T11:00,baixa\n"
        " 1 ,eq2,2024-01-03T10:00,2024-01-03T11:00,media\n",
    ]
    for trecho in ruins:
        with pytest.raises(ValueError):
            _rodar(tmp_path, CABECALHO + trecho)


def test_sla_invalido(tmp_path):
    csv_texto = CABECALHO + "1,eq,2024-01-01T00:00,2024-01-01T00:01,baixa\n"
    variantes = [
        {"limites_minutos": {"baixa": 10, "media": 10, "alta": 10, "urgente": 1}},
        {"limites_minutos": {"baixa": 10, "media": 10}},
        {"limites_minutos": {"baixa": 10, "media": 10, "alta": True}},
        {"limites_minutos": {"baixa": 10, "media": 10, "alta": 1.5}},
        {"limites_minutos": {"baixa": 0, "media": 10, "alta": 10}},
        {"outra": {}},
        ["baixa", "media", "alta"],
    ]
    for sla in variantes:
        with pytest.raises(ValueError):
            _rodar(tmp_path, csv_texto, sla=sla)


def test_cruza_meia_noite_e_piso_1_e_2(tmp_path):
    csv_texto = (
        CABECALHO
        + "p,n,2024-09-01T23:50,2024-09-02T00:10,alta\n"
        + "q,n,2024-09-01T00:00,2024-09-01T00:01,alta\n"
    )
    retorno, _ = _rodar(tmp_path, csv_texto)
    equipe = retorno["equipes"][0]
    assert equipe["tempo_medio_minutos"] == (20 + 1) // 2
    assert equipe["estourados"] == 0
    assert equipe["pior_id"] == "p"


def _texto_canonico(retorno):
    return json.dumps(retorno, ensure_ascii=False, indent=2) + "\n"


def test_json_exato_crlf_aspas_e_strip_agrupa(tmp_path):
    csv_texto = (
        "id,equipe,aberto_em,fechado_em,prioridade\r\n"
        'a10,"São, Paulo",2023-12-31T22:00,2024-01-01T00:00, alta \r\n'
        'a2," São, Paulo ",2024-01-01T00:00,2024-01-01T02:00,alta\r\n'
        ",,,,\r\n"
        "\r\n"
        "  a , n1 ,2024-05-01T00:00,2024-05-01T00:10,baixa\r\n"
    )
    retorno, texto = _rodar(tmp_path, csv_texto)
    assert texto == _texto_canonico(retorno)
    assert [item["equipe"] for item in retorno["equipes"]] == ["São, Paulo", "n1"]
    sao = retorno["equipes"][0]
    assert sao["chamados"] == 2
    assert sao["pior_id"] == "a10"
    assert sao["tempo_medio_minutos"] == (120 + 120) // 2
    assert sao["estourados"] == 2
    assert retorno["equipes"][1]["pior_id"] == "a"


def test_desempate_lexicografico_nao_numerico(tmp_path):
    csv_texto = (
        CABECALHO
        + "a2,eq,2024-04-01T00:00,2024-04-01T00:30,baixa\n"
        + "a10,eq,2024-04-01T00:00,2024-04-01T00:30,baixa\n"
        + "a1,eq,2024-04-01T00:00,2024-04-01T00:01,baixa\n"
    )
    retorno, texto = _rodar(tmp_path, csv_texto)
    assert retorno["equipes"][0]["pior_id"] == "a10"
    assert texto == _texto_canonico(retorno)


def test_ordem_de_code_point_sem_locale(tmp_path):
    csv_texto = (
        CABECALHO
        + "1,a,2024-01-01T00:00,2024-01-01T00:02,baixa\n"
        + "2,A,2024-01-01T00:00,2024-01-01T00:04,baixa\n"
        + "3,b,2024-01-01T00:00,2024-01-01T00:01,baixa\n"
    )
    retorno, _ = _rodar(tmp_path, csv_texto)
    assert [item["equipe"] for item in retorno["equipes"]] == ["A", "a", "b"]
    assert [item["pior_id"] for item in retorno["equipes"]] == ["2", "1", "3"]


def test_id_duplicado_so_depois_do_strip(tmp_path):
    csv_texto = (
        CABECALHO
        + "a,eq,2024-01-01T00:00,2024-01-01T00:01,baixa\n"
        + " a ,eq2,2024-01-02T00:00,2024-01-02T00:01,baixa\n"
    )
    with pytest.raises(ValueError):
        _rodar(tmp_path, csv_texto)


def test_id_com_espaco_interno_e_linha_de_virgulas(tmp_path):
    csv_texto = (
        CABECALHO
        + "a b,eq,2024-01-01T00:00,2024-01-01T00:03,media\n"
        + ",,,,\n"
        + "   \n"
    )
    retorno, _ = _rodar(tmp_path, csv_texto)
    assert retorno["equipes"][0]["pior_id"] == "a b"
    assert retorno["equipes"][0]["tempo_medio_minutos"] == 3
    assert retorno["equipes"][0]["estourados"] == 0


def test_vazio_bom_e_cabecalho_com_espaco(tmp_path):
    with pytest.raises(ValueError):
        _rodar(tmp_path, "")
    with pytest.raises(ValueError):
        _rodar(tmp_path, "id, equipe,aberto_em,fechado_em,prioridade\n")
    cru = CABECALHO + "1,eq,2024-01-01T00:00,2024-01-01T00:01,baixa\n"
    csv_path = tmp_path / "chamados.csv"
    sla_path = tmp_path / "sla.json"
    saida = tmp_path / "resumo.json"
    csv_path.write_bytes(b"\xef\xbb\xbf" + cru.encode("utf-8"))
    sla_path.write_text(json.dumps(SLA), encoding="utf-8")
    with pytest.raises(ValueError):
        consolidar(str(csv_path), str(sla_path), str(saida))
    csv_path.write_text(cru, encoding="utf-8")
    sla_path.write_bytes(b"\xef\xbb\xbf" + json.dumps(SLA).encode("utf-8"))
    with pytest.raises(ValueError):
        consolidar(str(csv_path), str(sla_path), str(saida))
    sla_path.write_text("", encoding="utf-8")
    with pytest.raises(ValueError):
        consolidar(str(csv_path), str(sla_path), str(saida))


def test_limite_exato_por_prioridade_e_ano(tmp_path):
    sla = {"limites_minutos": {"baixa": 1, "media": 100, "alta": 120}}
    csv_texto = (
        CABECALHO
        + "z,eq,2023-12-31T23:00,2024-01-01T01:00,alta\n"
        + "a,eq,2024-01-01T00:00,2024-01-01T00:01,baixa\n"
        + "m,eq,2024-01-01T00:00,2024-01-01T01:40,media\n"
    )
    retorno, _ = _rodar(tmp_path, csv_texto, sla=sla)
    equipe = retorno["equipes"][0]
    assert equipe["estourados"] == 0
    assert equipe["pior_id"] == "z"
    assert equipe["tempo_medio_minutos"] == (120 + 1 + 100) // 3


def test_muitas_linhas_preserva_totais(tmp_path):
    linhas = [
        f"id{i:04d},eq,2024-01-01T00:00,2024-01-01T00:{i % 60:02d},baixa"
        for i in range(30)
    ]
    retorno, texto = _rodar(tmp_path, CABECALHO + "\n".join(linhas) + "\n")
    duracoes = [i % 60 for i in range(30)]
    assert retorno["equipes"][0]["chamados"] == 30
    assert retorno["equipes"][0]["tempo_medio_minutos"] == sum(duracoes) // 30
    assert retorno["equipes"][0]["pior_id"] == "id0029"
    assert retorno["equipes"][0]["estourados"] == 0
    assert texto == _texto_canonico(retorno)


def test_sla_limite_negativo_e_csv_ausente_com_sla_presente(tmp_path):
    csv_texto = CABECALHO + "1,eq,2024-01-01T00:00,2024-01-01T00:01,baixa\n"
    with pytest.raises(ValueError):
        _rodar(
            tmp_path,
            csv_texto,
            sla={"limites_minutos": {"baixa": -1, "media": 10, "alta": 10}},
        )
    csv_path, sla_path, saida = _gravar(tmp_path, csv_texto)
    with pytest.raises(FileNotFoundError):
        consolidar(str(tmp_path / "nao.csv"), sla_path, saida)
