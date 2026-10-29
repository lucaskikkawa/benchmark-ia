"""Suíte de referência: cobre cada regra e cada fronteira do cupom."""

from datetime import date

import pytest

from descontos import aplicar_desconto

HOJE = "2024-06-15"


def _checar(preco, cupom, hoje, final, aplicado):
    resultado = aplicar_desconto(preco, cupom, hoje)
    assert set(resultado) == {"preco_final", "desconto", "cupom_aplicado"}
    assert resultado["preco_final"] == final
    assert resultado["desconto"] == preco - final
    assert resultado["cupom_aplicado"] == aplicado
    return resultado


def test_sem_cupom_none_ou_vazio():
    _checar(1500, None, HOJE, 1500, None)
    _checar(1500, "", HOJE, 1500, None)
    _checar(0, None, HOJE, 0, None)


def test_off10_piso():
    _checar(1000, "OFF10", HOJE, 900, "OFF10")
    _checar(1, "OFF10", HOJE, 0, "OFF10")
    _checar(0, "OFF10", HOJE, 0, "OFF10")


def test_off5_piso():
    _checar(200, "OFF5", HOJE, 190, "OFF5")
    _checar(101, "OFF5", HOJE, 95, "OFF5")


def test_fixo500_nao_fica_negativo():
    _checar(100, "FIXO500", HOJE, 0, "FIXO500")
    _checar(500, "FIXO500", HOJE, 0, "FIXO500")
    _checar(501, "FIXO500", HOJE, 1, "FIXO500")
    _checar(0, "FIXO500", HOJE, 0, "FIXO500")


def test_bemvindo_inclusive_nas_pontas():
    _checar(100, "BEMVINDO", "2024-01-01", 80, "BEMVINDO")
    _checar(100, "BEMVINDO", "2024-12-31", 80, "BEMVINDO")
    _checar(250, "BEMVINDO", "2024-06-15", 200, "BEMVINDO")


def test_bemvindo_fora_da_janela_nao_aplica():
    _checar(100, "BEMVINDO", "2023-12-31", 100, None)
    _checar(100, "BEMVINDO", "2025-01-01", 100, None)


def test_natal_24_e_25_em_qualquer_ano():
    _checar(100, "NATAL", "2024-12-24", 85, "NATAL")
    _checar(200, "NATAL", "1999-12-25", 170, "NATAL")
    _checar(100, "NATAL", "2024-12-23", 100, None)
    _checar(100, "NATAL", "2024-12-26", 100, None)


def test_cupom_desconhecido_e_caixa():
    with pytest.raises(ValueError):
        aplicar_desconto(100, "XYZ", HOJE)
    with pytest.raises(ValueError):
        aplicar_desconto(100, "off10", HOJE)
    with pytest.raises(ValueError):
        aplicar_desconto(100, " OFF10", HOJE)
    with pytest.raises(ValueError):
        aplicar_desconto(100, "OFF10 ", HOJE)


def test_preco_negativo_e_tipos():
    with pytest.raises(ValueError):
        aplicar_desconto(-1, None, HOJE)
    with pytest.raises(TypeError):
        aplicar_desconto(True, None, HOJE)
    with pytest.raises(TypeError):
        aplicar_desconto(10.0, None, HOJE)
    with pytest.raises(TypeError):
        aplicar_desconto(100, 10, HOJE)
    with pytest.raises(TypeError):
        aplicar_desconto(100, None, None)
    with pytest.raises(TypeError):
        aplicar_desconto(100, None, date(2024, 6, 15))


def test_data_invalida():
    for hoje in ("2024-02-30", "2023-02-29", "2024-1-01", "20240229", "2024/06/15", ""):
        with pytest.raises(ValueError):
            aplicar_desconto(100, None, hoje)


def test_ano_bissexto_valido_sem_cupom():
    _checar(80, None, "2024-02-29", 80, None)
