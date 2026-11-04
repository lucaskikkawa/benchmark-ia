"""Suíte de testes para o contrato de descontos.aplicar_desconto."""

from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
import sys
import pytest

_ROOT = str(Path(__file__).resolve().parent.parent)
if _ROOT not in sys.path:
    sys.path.append(_ROOT)

from descontos import aplicar_desconto


def _verificar_retorno(res, preco_centavos, preco_final_esperado, cupom_esperado):
    assert type(res) is dict
    assert set(res.keys()) == {"preco_final", "desconto", "cupom_aplicado"}
    assert type(res["preco_final"]) is int
    assert type(res["desconto"]) is int
    assert res["preco_final"] == preco_final_esperado
    assert res["desconto"] == preco_centavos - preco_final_esperado
    if cupom_esperado is None:
        assert res["cupom_aplicado"] is None
    else:
        assert type(res["cupom_aplicado"]) is str
        assert res["cupom_aplicado"] == cupom_esperado


class TestContratoRetorno:
    def test_chaves_e_tipos_exatos_com_cupom(self):
        res = aplicar_desconto(1000, "OFF10", "2024-06-15")
        _verificar_retorno(res, 1000, 900, "OFF10")

    def test_chaves_e_tipos_exatos_sem_cupom(self):
        res = aplicar_desconto(1000, None, "2024-06-15")
        _verificar_retorno(res, 1000, 1000, None)


class TestValidacaoPrecoCentavos:
    @pytest.mark.parametrize(
        "preco_invalido",
        [
            True,
            False,
            0.0,
            100.0,
            -1.0,
            10.5,
            "100",
            "0",
            None,
            [100],
            (100,),
            {"preco": 100},
            Decimal("100"),
            b"100",
        ],
    )
    def test_preco_tipo_invalido_levanta_type_error(self, preco_invalido):
        with pytest.raises(TypeError):
            aplicar_desconto(preco_invalido, "OFF10", "2024-06-15")
        with pytest.raises(TypeError):
            aplicar_desconto(preco_invalido, None, "2024-06-15")

    @pytest.mark.parametrize("preco_negativo", [-1, -2, -10, -100, -500, -999999])
    def test_preco_negativo_levanta_value_error(self, preco_negativo):
        with pytest.raises(ValueError):
            aplicar_desconto(preco_negativo, "OFF10", "2024-06-15")
        with pytest.raises(ValueError):
            aplicar_desconto(preco_negativo, None, "2024-06-15")
        with pytest.raises(ValueError):
            aplicar_desconto(preco_negativo, "FIXO500", "2024-06-15")


class TestValidacaoCupom:
    @pytest.mark.parametrize(
        "cupom_tipo_invalido",
        [
            0,
            10,
            -1,
            True,
            False,
            10.0,
            ["OFF10"],
            ("OFF10",),
            {"cupom": "OFF10"},
            b"OFF10",
        ],
    )
    def test_cupom_tipo_invalido_levanta_type_error(self, cupom_tipo_invalido):
        with pytest.raises(TypeError):
            aplicar_desconto(1000, cupom_tipo_invalido, "2024-06-15")
        with pytest.raises(TypeError):
            aplicar_desconto(0, cupom_tipo_invalido, "2024-06-15")

    @pytest.mark.parametrize("preco", [0, 1, 100, 1234])
    def test_cupom_none_nao_altera_preco(self, preco):
        res = aplicar_desconto(preco, None, "2024-06-15")
        _verificar_retorno(res, preco, preco, None)

    @pytest.mark.parametrize("preco", [0, 1, 100, 1234])
    def test_cupom_string_vazia_nao_altera_preco_e_retorna_none(self, preco):
        res = aplicar_desconto(preco, "", "2024-06-15")
        _verificar_retorno(res, preco, preco, None)

    @pytest.mark.parametrize(
        "cupom_desconhecido",
        [
            " ",
            "  ",
            "\t",
            "\n",
            "\r",
            " \t\n ",
            " OFF10",
            "OFF10 ",
            " OFF10 ",
            "\tOFF10",
            "OFF10\n",
            "off10",
            "Off10",
            "oFF10",
            " OFF5",
            "OFF5 ",
            "off5",
            "Off5",
            " FIXO500",
            "FIXO500 ",
            "fixo500",
            "Fixo500",
            " BEMVINDO",
            "BEMVINDO ",
            "bemvindo",
            "Bemvindo",
            " NATAL",
            "NATAL ",
            "natal",
            "Natal",
            "OFF0",
            "OFF15",
            "OFF20",
            "OFF50",
            "OFF100",
            "FIXO100",
            "FIXO0",
            "DESCONTO",
            "CUPOM",
            "NONE",
            "None",
            "null",
            "OFF10\x00",
        ],
    )
    def test_cupom_desconhecido_ou_com_espaco_ou_minusculo_levanta_value_error(
        self, cupom_desconhecido
    ):
        with pytest.raises(ValueError):
            aplicar_desconto(1000, cupom_desconhecido, "2024-12-25")
        with pytest.raises(ValueError):
            aplicar_desconto(0, cupom_desconhecido, "2024-12-25")


class TestValidacaoDataHoje:
    @pytest.mark.parametrize(
        "hoje_tipo_invalido",
        [
            None,
            20240101,
            2024,
            True,
            False,
            2024.01,
            date(2024, 1, 1),
            datetime(2024, 1, 1, 0, 0),
            ["2024-01-01"],
            ("2024-01-01",),
            {"hoje": "2024-01-01"},
            b"2024-01-01",
        ],
    )
    @pytest.mark.parametrize("cupom", [None, "", "OFF10", "BEMVINDO", "NATAL"])
    def test_hoje_tipo_invalido_levanta_type_error(self, hoje_tipo_invalido, cupom):
        with pytest.raises(TypeError):
            aplicar_desconto(1000, cupom, hoje_tipo_invalido)

    @pytest.mark.parametrize(
        "data_invalida",
        [
            "",
            " ",
            "20240101",
            "2024-W01-1",
            "2024/01/01",
            "2024.01.01",
            "2024_01_01",
            "2024-1-1",
            "2024-01-1",
            "2024-1-01",
            "24-01-01",
            "024-01-01",
            "10000-01-01",
            "0000-01-01",
            "-001-01-01",
            "+024-01-01",
            "+202-01-01",
            "2024-+1-01",
            "2024-01-+1",
            "2024--1-01",
            "2024-01--1",
            "01-01-2024",
            "25-12-2024",
            "12-25-2024",
            "2024-01-01T00:00:00",
            "2024-01-01 00:00:00",
            " 2024-01-01",
            "2024-01-01 ",
            "2024-01-01\n",
            "\n2024-01-01",
            "abcd-ef-gh",
            "2024-01-0a",
            "----------",
            "2024-00-01",
            "2024-13-01",
            "2024-99-01",
            "2024-01-00",
            "2024-01-32",
            "2024-02-30",
            "2024-02-31",
            "2023-02-29",
            "2025-02-29",
            "1900-02-29",
            "2100-02-29",
            "1800-02-29",
            "2200-02-29",
            "2300-02-29",
            "2024-04-31",
            "2024-06-31",
            "2024-09-31",
            "2024-11-31",
            "٢٠٢٤-٠١-٠١",
        ],
    )
    @pytest.mark.parametrize("cupom", [None, "", "OFF10", "OFF5", "FIXO500", "BEMVINDO", "NATAL"])
    def test_hoje_formato_ou_calendario_invalido_levanta_value_error(
        self, data_invalida, cupom
    ):
        with pytest.raises(ValueError):
            aplicar_desconto(1000, cupom, data_invalida)

    @pytest.mark.parametrize(
        "data_valida",
        [
            "0001-01-01",
            "0001-12-25",
            "0004-02-29",
            "0400-02-29",
            "1600-02-29",
            "2000-02-29",
            "2024-02-29",
            "2400-02-29",
            "9999-12-31",
            "2024-01-31",
            "2024-03-31",
            "2024-04-30",
            "2024-05-31",
            "2024-06-30",
            "2024-07-31",
            "2024-08-31",
            "2024-09-30",
            "2024-10-31",
            "2024-11-30",
            "2024-12-31",
        ],
    )
    def test_datas_validas_bissextas_e_extremos(self, data_valida):
        res = aplicar_desconto(1000, "OFF10", data_valida)
        _verificar_retorno(res, 1000, 900, "OFF10")


class TestCupomOFF10:
    @pytest.mark.parametrize(
        "preco,esperado_final",
        [
            (0, 0),
            (1, 0),
            (2, 1),
            (5, 4),
            (9, 8),
            (10, 9),
            (11, 9),
            (15, 13),
            (19, 17),
            (20, 18),
            (99, 89),
            (100, 90),
            (101, 90),
            (105, 94),
            (109, 98),
            (110, 99),
            (111, 99),
            (200, 180),
            (999, 899),
            (1000, 900),
            (9999999999999995, 8999999999999995),
        ],
    )
    def test_calculo_off10_piso_exato(self, preco, esperado_final):
        res = aplicar_desconto(preco, "OFF10", "2024-05-10")
        _verificar_retorno(res, preco, esperado_final, "OFF10")


class TestCupomOFF5:
    @pytest.mark.parametrize(
        "preco,esperado_final",
        [
            (0, 0),
            (1, 0),
            (2, 1),
            (10, 9),
            (19, 18),
            (20, 19),
            (21, 19),
            (30, 28),
            (39, 37),
            (40, 38),
            (50, 47),
            (99, 94),
            (100, 95),
            (101, 95),
            (119, 113),
            (120, 114),
            (199, 189),
            (200, 190),
            (201, 190),
            (1000, 950),
            (9999999999999995, 9499999999999995),
        ],
    )
    def test_calculo_off5_piso_exato(self, preco, esperado_final):
        res = aplicar_desconto(preco, "OFF5", "2023-08-20")
        _verificar_retorno(res, preco, esperado_final, "OFF5")


class TestCupomFIXO500:
    @pytest.mark.parametrize(
        "preco,esperado_final,esperado_desconto",
        [
            (0, 0, 0),
            (1, 0, 1),
            (50, 0, 50),
            (100, 0, 100),
            (250, 0, 250),
            (499, 0, 499),
            (500, 0, 500),
            (501, 1, 500),
            (502, 2, 500),
            (600, 100, 500),
            (1000, 500, 500),
            (10000, 9500, 500),
        ],
    )
    def test_calculo_fixo500_com_piso_zero(
        self, preco, esperado_final, esperado_desconto
    ):
        res = aplicar_desconto(preco, "FIXO500", "2025-03-15")
        _verificar_retorno(res, preco, esperado_final, "FIXO500")
        assert res["desconto"] == esperado_desconto


class TestCupomBEMVINDO:
    @pytest.mark.parametrize(
        "data_dentro",
        [
            "2024-01-01",
            "2024-01-02",
            "2024-02-28",
            "2024-02-29",
            "2024-06-15",
            "2024-12-24",
            "2024-12-25",
            "2024-12-30",
            "2024-12-31",
        ],
    )
    @pytest.mark.parametrize(
        "preco,esperado_final",
        [
            (0, 0),
            (1, 0),
            (2, 1),
            (4, 3),
            (5, 4),
            (6, 4),
            (9, 7),
            (10, 8),
            (11, 8),
            (99, 79),
            (100, 80),
            (101, 80),
            (200, 160),
            (1000, 800),
            (9999999999999995, 7999999999999996),
        ],
    )
    def test_bemvindo_dentro_da_janela_2024(self, data_dentro, preco, esperado_final):
        res = aplicar_desconto(preco, "BEMVINDO", data_dentro)
        _verificar_retorno(res, preco, esperado_final, "BEMVINDO")

    @pytest.mark.parametrize(
        "data_fora",
        [
            "0001-01-01",
            "0001-12-31",
            "2000-02-29",
            "2023-01-01",
            "2023-06-15",
            "2023-12-30",
            "2023-12-31",
            "2025-01-01",
            "2025-01-02",
            "2025-06-15",
            "2025-12-25",
            "2025-12-31",
            "9999-01-01",
            "9999-12-31",
        ],
    )
    @pytest.mark.parametrize("preco", [0, 1, 100, 1000])
    def test_bemvindo_fora_da_janela_nao_aplica_nem_levanta_erro(
        self, data_fora, preco
    ):
        res = aplicar_desconto(preco, "BEMVINDO", data_fora)
        _verificar_retorno(res, preco, preco, None)


class TestCupomNATAL:
    @pytest.mark.parametrize(
        "data_natal",
        [
            "0001-12-24",
            "0001-12-25",
            "1900-12-24",
            "1900-12-25",
            "2000-12-24",
            "2000-12-25",
            "2023-12-24",
            "2023-12-25",
            "2024-12-24",
            "2024-12-25",
            "2025-12-24",
            "2025-12-25",
            "9999-12-24",
            "9999-12-25",
        ],
    )
    @pytest.mark.parametrize(
        "preco,esperado_final",
        [
            (0, 0),
            (1, 0),
            (2, 1),
            (6, 5),
            (7, 5),
            (10, 8),
            (19, 16),
            (20, 17),
            (21, 17),
            (99, 84),
            (100, 85),
            (101, 85),
            (200, 170),
            (1000, 850),
            (9999999999999995, 8499999999999995),
        ],
    )
    def test_natal_em_24_e_25_de_dezembro_qualquer_ano(
        self, data_natal, preco, esperado_final
    ):
        res = aplicar_desconto(preco, "NATAL", data_natal)
        _verificar_retorno(res, preco, esperado_final, "NATAL")

    @pytest.mark.parametrize(
        "data_nao_natal",
        [
            "0001-01-01",
            "0001-12-23",
            "0001-12-26",
            "2023-12-23",
            "2023-12-26",
            "2024-01-24",
            "2024-01-25",
            "2024-06-24",
            "2024-06-25",
            "2024-11-24",
            "2024-11-25",
            "2024-12-01",
            "2024-12-23",
            "2024-12-26",
            "2024-12-31",
            "2025-12-23",
            "2025-12-26",
            "9999-12-23",
            "9999-12-26",
            "9999-12-31",
        ],
    )
    @pytest.mark.parametrize("preco", [0, 1, 100, 1000])
    def test_natal_fora_de_24_e_25_dezembro_nao_aplica_nem_levanta_erro(
        self, data_nao_natal, preco
    ):
        res = aplicar_desconto(preco, "NATAL", data_nao_natal)
        _verificar_retorno(res, preco, preco, None)
