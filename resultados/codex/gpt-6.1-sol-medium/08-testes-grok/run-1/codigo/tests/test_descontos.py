from datetime import date, timedelta

import pytest

from descontos import aplicar_desconto


def conferir(preco, cupom, hoje, final, aplicado):
    resultado = aplicar_desconto(preco, cupom, hoje)
    assert type(resultado) is dict
    assert resultado == {
        "preco_final": final,
        "desconto": preco - final,
        "cupom_aplicado": aplicado,
    }
    assert type(resultado["preco_final"]) is int
    assert type(resultado["desconto"]) is int
    assert resultado["cupom_aplicado"] is None or type(resultado["cupom_aplicado"]) is str


PRECOS = list(range(201)) + [499, 500, 501, 999, 1000, 1001, 10001, 10**30 + 37]
CUPONS = [None, "", "OFF10", "OFF5", "FIXO500", "BEMVINDO", "NATAL"]


@pytest.mark.parametrize("preco", PRECOS)
@pytest.mark.parametrize("cupom", [None, ""])
def test_sem_cupom(preco, cupom):
    conferir(preco, cupom, "2024-12-25", preco, None)


@pytest.mark.parametrize("preco", PRECOS)
@pytest.mark.parametrize("cupom,percentual", [("OFF10", 90), ("OFF5", 95)])
def test_percentuais_permanentes(preco, cupom, percentual):
    conferir(preco, cupom, "2025-06-17", preco * percentual // 100, cupom)


@pytest.mark.parametrize("preco", PRECOS)
def test_fixo_com_limite_no_valor_do_preco(preco):
    conferir(preco, "FIXO500", "2024-01-01", max(0, preco - 500), "FIXO500")


@pytest.mark.parametrize("preco", [0, 1, 2, 99, 100, 101, 501, 10**30 + 37])
@pytest.mark.parametrize(
    "hoje,ativo",
    [
        ("0001-01-01", False),
        ("2023-01-01", False),
        ("2023-12-31", False),
        ("2024-01-01", True),
        ("2024-01-02", True),
        ("2024-02-29", True),
        ("2024-06-15", True),
        ("2024-12-30", True),
        ("2024-12-31", True),
        ("2025-01-01", False),
        ("2025-12-31", False),
        ("9999-12-31", False),
    ],
)
def test_janela_bemvindo(preco, hoje, ativo):
    conferir(preco, "BEMVINDO", hoje, preco * 80 // 100 if ativo else preco,
             "BEMVINDO" if ativo else None)


@pytest.mark.parametrize("ano", [1, 4, 1900, 2000, 2023, 2024, 2025, 2100, 9999])
@pytest.mark.parametrize("mes,dia", [(12, 23), (12, 24), (12, 25), (12, 26), (11, 24), (11, 25), (1, 1)])
@pytest.mark.parametrize("preco", [0, 1, 99, 100, 101, 501, 10**30 + 37])
def test_natal_em_qualquer_ano(preco, ano, mes, dia):
    ativo = mes == 12 and dia in (24, 25)
    conferir(preco, "NATAL", f"{ano:04d}-{mes:02d}-{dia:02d}",
             preco * 85 // 100 if ativo else preco, "NATAL" if ativo else None)


def test_calendario_inteiro_das_promocoes():
    primeiro = date(2023, 1, 1)
    ultimo = date(2025, 12, 31)
    for deslocamento in range((ultimo - primeiro).days + 1):
        dia = primeiro + timedelta(days=deslocamento)
        for cupom, percentual, ativo in [
            ("BEMVINDO", 80, dia.year == 2024),
            ("NATAL", 85, dia.month == 12 and dia.day in (24, 25)),
        ]:
            conferir(107, cupom, dia.isoformat(), 107 * percentual // 100 if ativo else 107,
                     cupom if ativo else None)


@pytest.mark.parametrize("cupom", [" ", "\t", "\n", "off10", "Off10", " OFF10", "OFF10 ",
                                  "OFF10\n", "OFF 10", "OFF15", "OFF50", "FIXO", "bemvindo", "natal", "INVALIDO"])
def test_codigo_precisa_ser_exato(cupom):
    with pytest.raises(ValueError):
        aplicar_desconto(1000, cupom, "2024-12-25")


@pytest.mark.parametrize("cupom", CUPONS)
@pytest.mark.parametrize("preco", [True, False, 0.0, 1.0, -1.5, "100", None, [], {}, complex(1, 0)])
def test_tipo_invalido_de_preco(preco, cupom):
    with pytest.raises(TypeError):
        aplicar_desconto(preco, cupom, "2024-06-15")


@pytest.mark.parametrize("cupom", CUPONS)
@pytest.mark.parametrize("preco", [-1, -500, -10**30])
def test_preco_negativo(preco, cupom):
    with pytest.raises(ValueError):
        aplicar_desconto(preco, cupom, "2024-06-15")


@pytest.mark.parametrize("cupom", [False, True, 0, 1, 1.0, [], {}, b"OFF10"])
def test_tipo_invalido_de_cupom(cupom):
    with pytest.raises(TypeError):
        aplicar_desconto(1000, cupom, "2024-06-15")


@pytest.mark.parametrize("cupom", CUPONS)
@pytest.mark.parametrize("hoje", [None, True, 20240101, 2024.0, date(2024, 1, 1), [], {}, b"2024-01-01"])
def test_tipo_invalido_de_data(hoje, cupom):
    with pytest.raises(TypeError):
        aplicar_desconto(1000, cupom, hoje)


@pytest.mark.parametrize("cupom", CUPONS)
@pytest.mark.parametrize("hoje", [
    "", " ", "20240101", "2024-1-01", "2024-01-1", "24-01-01",
    "2024/01/01", "2024.01.01", "2024-01/01", "2024/01-01",
    " 2024-01-01", "2024-01-01 ", "2024-01-01\n", "2024-01-01T00:00:00",
    "abcd-ef-gh", "2024-00-01", "2024-13-01", "2024-01-00", "2024-01-32",
    "2024-04-31", "2024-06-31", "2024-09-31", "2024-11-31", "2024-02-30",
    "2023-02-29", "1900-02-29", "2100-02-29", "0001-02-29", "0000-01-01",
    "10000-01-01", "-001-01-01", "2024-W01-1",
])
def test_datas_invalidas_mesmo_sem_promocao_ativa(hoje, cupom):
    with pytest.raises(ValueError):
        aplicar_desconto(1000, cupom, hoje)


@pytest.mark.parametrize("cupom", [None, "", "OFF10", "OFF5", "FIXO500", "BEMVINDO", "NATAL"])
@pytest.mark.parametrize("hoje", ["0001-01-01", "0004-02-29", "1600-02-29", "1900-02-28",
                                  "2000-02-29", "2024-02-29", "2100-03-01", "2400-02-29", "9999-12-31"])
def test_datas_gregorianas_validas(hoje, cupom):
    finais = {None: 101, "": 101, "OFF10": 90, "OFF5": 95, "FIXO500": 0,
              "BEMVINDO": 80 if hoje == "2024-02-29" else 101, "NATAL": 101}
    aplicado = cupom if cupom in ("OFF10", "OFF5", "FIXO500") else None
    if cupom == "BEMVINDO" and hoje == "2024-02-29":
        aplicado = cupom
    conferir(101, cupom, hoje, finais[cupom], aplicado)
