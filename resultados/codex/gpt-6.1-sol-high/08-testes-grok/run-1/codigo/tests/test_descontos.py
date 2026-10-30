"""Testes do contrato público de aplicar_desconto."""

from datetime import date

import pytest

from descontos import aplicar_desconto


CUPONS = (None, "", "OFF10", "OFF5", "FIXO500", "BEMVINDO", "NATAL")
PRECOS = tuple(range(202)) + (
    499, 500, 501, 502, 999, 1000, 1001, 1999, 10001,
    2**53 - 1, 2**53 + 1, 10**30 + 99,
)


def conferir(preco, cupom, hoje, final, aplicado):
    resultado = aplicar_desconto(preco, cupom, hoje)
    assert type(resultado) is dict
    assert resultado == {
        "preco_final": final,
        "desconto": preco - final,
        "cupom_aplicado": aplicado,
    }
    # Igualdade numérica sozinha também aceitaria floats e bools.
    assert type(resultado["preco_final"]) is int
    assert type(resultado["desconto"]) is int
    if aplicado is not None:
        assert type(resultado["cupom_aplicado"]) is str
    else:
        assert resultado["cupom_aplicado"] is None


@pytest.mark.parametrize("preco", PRECOS)
@pytest.mark.parametrize("cupom", (None, ""))
def test_sem_cupom(preco, cupom):
    conferir(preco, cupom, "2024-12-25", preco, None)


@pytest.mark.parametrize("preco", PRECOS)
@pytest.mark.parametrize(
    "cupom,hoje,percentual_restante",
    (
        ("OFF10", "2025-06-15", 90),
        ("OFF5", "2023-06-15", 95),
        ("BEMVINDO", "2024-06-15", 80),
        ("NATAL", "2025-12-24", 85),
        ("NATAL", "2025-12-25", 85),
    ),
)
def test_percentuais_com_piso(preco, cupom, hoje, percentual_restante):
    final = (preco * percentual_restante) // 100
    conferir(preco, cupom, hoje, final, cupom)


@pytest.mark.parametrize("preco", PRECOS)
def test_fixo500_inclusive_piso_e_preco_zero(preco):
    final = 0 if preco <= 500 else preco - 500
    conferir(preco, "FIXO500", "2024-01-01", final, "FIXO500")


@pytest.mark.parametrize("preco", (0, 1, 101, 1000))
@pytest.mark.parametrize(
    "hoje,ativo",
    (
        ("0001-01-01", False),
        ("2023-01-01", False),
        ("2023-12-31", False),
        ("2024-01-01", True),
        ("2024-01-02", True),
        ("2024-02-29", True),
        ("2024-06-30", True),
        ("2024-12-30", True),
        ("2024-12-31", True),
        ("2025-01-01", False),
        ("2025-12-31", False),
        ("9999-12-31", False),
    ),
)
def test_janela_bemvindo(preco, hoje, ativo):
    conferir(
        preco, "BEMVINDO", hoje,
        (preco * 80) // 100 if ativo else preco,
        "BEMVINDO" if ativo else None,
    )


@pytest.mark.parametrize("ano", (1, 4, 100, 400, 1900, 2000, 2023, 2024, 2100, 9999))
@pytest.mark.parametrize("mes", range(1, 13))
@pytest.mark.parametrize("dia", (1, 23, 24, 25, 26, 28))
@pytest.mark.parametrize("preco", (0, 1, 101))
def test_natal_somente_24_e_25_de_dezembro_em_qualquer_ano(ano, mes, dia, preco):
    hoje = f"{ano:04d}-{mes:02d}-{dia:02d}"
    ativo = mes == 12 and dia in (24, 25)
    conferir(
        preco, "NATAL", hoje,
        (preco * 85) // 100 if ativo else preco,
        "NATAL" if ativo else None,
    )


@pytest.mark.parametrize("cupom", CUPONS)
@pytest.mark.parametrize(
    "hoje",
    (
        "0001-01-01", "0001-12-25", "0004-02-29", "0400-02-29",
        "1600-02-29", "1900-02-28", "1900-03-01", "2000-02-29",
        "2024-02-29", "2100-02-28", "2100-03-01", "2400-02-29",
        "9999-12-24", "9999-12-25", "9999-12-31",
    ),
)
def test_datas_validas_do_calendario_gregoriano(cupom, hoje):
    if cupom == "OFF10":
        final, aplicado = 909, cupom
    elif cupom == "OFF5":
        final, aplicado = 960, cupom
    elif cupom == "FIXO500":
        final, aplicado = 511, cupom
    elif cupom == "BEMVINDO" and hoje[:4] == "2024":
        final, aplicado = 808, cupom
    elif cupom == "NATAL" and hoje[5:] in ("12-24", "12-25"):
        final, aplicado = 859, cupom
    else:
        final, aplicado = 1011, None
    conferir(1011, cupom, hoje, final, aplicado)


@pytest.mark.parametrize("cupom", CUPONS)
@pytest.mark.parametrize(
    "preco",
    (True, False, 0.0, 1.0, 1.5, float("inf"), float("nan"),
     None, "100", b"100", [], {}, (), complex(100, 0)),
)
def test_preco_exige_int_e_rejeita_bool(cupom, preco):
    with pytest.raises(TypeError):
        aplicar_desconto(preco, cupom, "2024-12-25")


@pytest.mark.parametrize("cupom", CUPONS)
@pytest.mark.parametrize("preco", (-1, -500, -10000, -(10**30)))
def test_preco_negativo(cupom, preco):
    with pytest.raises(ValueError):
        aplicar_desconto(preco, cupom, "2024-12-25")


@pytest.mark.parametrize("cupom", (False, True, 0, 1, 0.0, [], {}, (), b"OFF10"))
@pytest.mark.parametrize("preco", (0, 1000))
def test_tipo_de_cupom(cupom, preco):
    with pytest.raises(TypeError):
        aplicar_desconto(preco, cupom, "2024-12-25")


@pytest.mark.parametrize(
    "cupom",
    (
        " ", "\t", "\n", "INEXISTENTE", "OFF", "OFF0", "OFF100", "off10",
        "Off10", "off5", "fixo500", "bemvindo", "natal", " OFF10", "OFF10 ",
        "OFF5\t", "\nFIXO500", " BEMVINDO ", "NATAL\n", "OFF10\0",
        "OFF10OFF5", "OFF10,NATAL", "０ＦＦ１０",
    ),
)
@pytest.mark.parametrize("preco", (0, 1000))
@pytest.mark.parametrize("hoje", ("2024-12-25", "2025-06-01"))
def test_texto_desconhecido_nao_e_normalizado(cupom, preco, hoje):
    with pytest.raises(ValueError):
        aplicar_desconto(preco, cupom, hoje)


@pytest.mark.parametrize("cupom", CUPONS)
@pytest.mark.parametrize(
    "hoje",
    (None, False, True, 20241225, 2024.0, b"2024-12-25", [], {}, (),
     date(2024, 12, 25)),
)
def test_data_exige_string_mesmo_sem_desconto(cupom, hoje):
    with pytest.raises(TypeError):
        aplicar_desconto(1000, cupom, hoje)


DATAS_INVALIDAS = (
    "", " ", "\t", "2024", "2024-01", "20240101", "2024-W01-1",
    "2024-1-01", "2024-01-1", "24-01-01", "02024-01-01",
    "2024/01/01", "2024.01.01", "2024_01_01", "2024-01/01",
    "2024/01-01", "01-01-2024", "2024-01-01 ", " 2024-01-01",
    "2024-01-01\n", "2024-01-01T00:00:00", "2024-01-01Z",
    "abcd-ef-gh", "２０２４-０１-０１", "2024-0x-01", "2024-01-xx",
    "0000-01-01", "10000-01-01", "-001-01-01", "+024-01-01",
    "2024-00-01", "2024-13-01", "2024-01-00", "2024-01-32",
    "2024-04-31", "2024-06-31", "2024-09-31", "2024-11-31",
    "2024-02-30", "2024-02-31", "2023-02-29", "0001-02-29",
    "0100-02-29", "1500-02-29", "1700-02-29", "1800-02-29",
    "1900-02-29", "2100-02-29", "2200-02-29", "2300-02-29",
    "9999-02-29", "9999-12-32",
)


@pytest.mark.parametrize("cupom", CUPONS)
@pytest.mark.parametrize("hoje", DATAS_INVALIDAS)
@pytest.mark.parametrize("preco", (0, 1000))
def test_data_invalida_mesmo_com_cupom_vazio_ou_preco_zero(cupom, hoje, preco):
    with pytest.raises(ValueError):
        aplicar_desconto(preco, cupom, hoje)
