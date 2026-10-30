from datetime import date, datetime
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from descontos import aplicar_desconto


class TestEstruturaRetorno:
    def test_chaves_e_tipos_do_retorno_com_cupom(self):
        resultado = aplicar_desconto(1000, "OFF10", "2024-05-10")
        assert isinstance(resultado, dict)
        assert set(resultado.keys()) == {"preco_final", "desconto", "cupom_aplicado"}
        assert type(resultado["preco_final"]) is int
        assert type(resultado["desconto"]) is int
        assert resultado["cupom_aplicado"] == "OFF10"
        assert resultado["desconto"] == 1000 - resultado["preco_final"]

    def test_chaves_e_tipos_do_retorno_sem_cupom(self):
        resultado = aplicar_desconto(1000, None, "2024-05-10")
        assert isinstance(resultado, dict)
        assert set(resultado.keys()) == {"preco_final", "desconto", "cupom_aplicado"}
        assert type(resultado["preco_final"]) is int
        assert type(resultado["desconto"]) is int
        assert resultado["preco_final"] == 1000
        assert resultado["desconto"] == 0
        assert resultado["cupom_aplicado"] is None


class TestValidacaoPreco:
    @pytest.mark.parametrize(
        "preco_invalido",
        [
            True,
            False,
            0.0,
            100.0,
            19.99,
            -0.5,
            "100",
            "0",
            None,
            [100],
            (100,),
            {"preco": 100},
        ],
    )
    def test_preco_tipo_invalido_levanta_type_error(self, preco_invalido):
        with pytest.raises(TypeError):
            aplicar_desconto(preco_invalido, "OFF10", "2024-06-01")
        with pytest.raises(TypeError):
            aplicar_desconto(preco_invalido, None, "2024-06-01")

    @pytest.mark.parametrize("preco_negativo", [-1, -2, -100, -500, -999999])
    def test_preco_negativo_levanta_value_error(self, preco_negativo):
        with pytest.raises(ValueError):
            aplicar_desconto(preco_negativo, "OFF10", "2024-06-01")
        with pytest.raises(ValueError):
            aplicar_desconto(preco_negativo, None, "2024-06-01")
        with pytest.raises(ValueError):
            aplicar_desconto(preco_negativo, "", "2024-06-01")


class TestValidacaoCupom:
    @pytest.mark.parametrize(
        "cupom_invalido",
        [
            0,
            10,
            True,
            False,
            10.5,
            b"OFF10",
            ["OFF10"],
            ("OFF10",),
            {"cupom": "OFF10"},
        ],
    )
    def test_cupom_tipo_invalido_levanta_type_error(self, cupom_invalido):
        with pytest.raises(TypeError):
            aplicar_desconto(1000, cupom_invalido, "2024-06-01")

    @pytest.mark.parametrize("cupom_vazio", [None, ""])
    @pytest.mark.parametrize("preco", [0, 1, 100, 500, 12345])
    def test_cupom_none_ou_string_vazia_nao_aplica_desconto(self, cupom_vazio, preco):
        resultado = aplicar_desconto(preco, cupom_vazio, "2024-06-01")
        assert resultado == {
            "preco_final": preco,
            "desconto": 0,
            "cupom_aplicado": None,
        }

    @pytest.mark.parametrize(
        "cupom_desconhecido",
        [
            " ",
            "  ",
            "\t",
            "\n",
            " OFF10",
            "OFF10 ",
            " OFF10 ",
            "\tOFF10",
            "OFF10\n",
            "off10",
            "Off10",
            "off5",
            "Off5",
            " OFF5",
            "OFF5 ",
            "fixo500",
            "Fixo500",
            " FIXO500",
            "FIXO500 ",
            "bemvindo",
            "BemVindo",
            " BEMVINDO",
            "BEMVINDO ",
            "natal",
            "Natal",
            " NATAL",
            "NATAL ",
            "OFF20",
            "OFF15",
            "FIXO100",
            "DESCONTO",
            "INVALIDO",
            "NONE",
            "null",
        ],
    )
    def test_cupom_desconhecido_ou_com_espaco_ou_minusculo_levanta_value_error(
        self, cupom_desconhecido
    ):
        with pytest.raises(ValueError):
            aplicar_desconto(1000, cupom_desconhecido, "2024-12-25")


class TestValidacaoData:
    @pytest.mark.parametrize(
        "hoje_invalido",
        [
            None,
            20240101,
            2024.01,
            True,
            False,
            date(2024, 1, 1),
            datetime(2024, 1, 1, 12, 0),
            b"2024-01-01",
            ["2024-01-01"],
        ],
    )
    def test_hoje_tipo_invalido_levanta_type_error(self, hoje_invalido):
        with pytest.raises(TypeError):
            aplicar_desconto(1000, "OFF10", hoje_invalido)
        with pytest.raises(TypeError):
            aplicar_desconto(1000, None, hoje_invalido)

    @pytest.mark.parametrize(
        "data_invalida",
        [
            "",
            "20240101",
            "2024-W01-1",
            "2024/01/01",
            "2024/01-01",
            "2024-01/01",
            "2024.01.01",
            "2024_01_01",
            "01-01-2024",
            "2024-1-01",
            "2024-01-1",
            "24-01-01",
            "2024-01-01 ",
            " 2024-01-01",
            "2024-01-01T00:00:00",
            "0000-01-01",
            "10000-01-01",
            "-001-01-01",
            "2024-00-01",
            "2024-13-01",
            "2024-01-00",
            "2024-01-32",
            "2024-02-30",
            "2023-02-29",
            "1900-02-29",
            "2100-02-29",
            "1800-02-29",
            "2024-04-31",
            "2024-06-31",
            "2024-09-31",
            "2024-11-31",
            "abcd-ef-gh",
            "2024-ab-01",
            "2024-01-cd",
            "+024-01-01",
        ],
    )
    def test_hoje_formato_ou_calendario_invalido_levanta_value_error(
        self, data_invalida
    ):
        with pytest.raises(ValueError):
            aplicar_desconto(1000, "OFF10", data_invalida)
        with pytest.raises(ValueError):
            aplicar_desconto(1000, None, data_invalida)
        with pytest.raises(ValueError):
            aplicar_desconto(1000, "", data_invalida)

    @pytest.mark.parametrize(
        "data_valida",
        [
            "0001-01-01",
            "0001-12-25",
            "2000-02-29",
            "2024-02-29",
            "2400-02-29",
            "9999-12-31",
        ],
    )
    def test_datas_validas_bissextas_e_extremos(self, data_valida):
        resultado = aplicar_desconto(1000, "OFF10", data_valida)
        assert resultado == {
            "preco_final": 900,
            "desconto": 100,
            "cupom_aplicado": "OFF10",
        }


class TestCupomOff10:
    @pytest.mark.parametrize(
        ("preco", "final_esperado", "desconto_esperado"),
        [
            (0, 0, 0),
            (1, 0, 1),
            (2, 1, 1),
            (9, 8, 1),
            (10, 9, 1),
            (11, 9, 2),
            (55, 49, 6),
            (99, 89, 10),
            (100, 90, 10),
            (101, 90, 11),
            (105, 94, 11),
            (1000, 900, 100),
        ],
    )
    def test_calculo_off10_com_piso(self, preco, final_esperado, desconto_esperado):
        resultado = aplicar_desconto(preco, "OFF10", "2023-05-10")
        assert resultado == {
            "preco_final": final_esperado,
            "desconto": desconto_esperado,
            "cupom_aplicado": "OFF10",
        }


class TestCupomOff5:
    @pytest.mark.parametrize(
        ("preco", "final_esperado", "desconto_esperado"),
        [
            (0, 0, 0),
            (1, 0, 1),
            (19, 18, 1),
            (20, 19, 1),
            (21, 19, 2),
            (99, 94, 5),
            (100, 95, 5),
            (101, 95, 6),
            (199, 189, 10),
            (200, 190, 10),
            (201, 190, 11),
            (1000, 950, 50),
        ],
    )
    def test_calculo_off5_com_piso(self, preco, final_esperado, desconto_esperado):
        resultado = aplicar_desconto(preco, "OFF5", "2025-08-20")
        assert resultado == {
            "preco_final": final_esperado,
            "desconto": desconto_esperado,
            "cupom_aplicado": "OFF5",
        }


class TestCupomFixo500:
    @pytest.mark.parametrize(
        ("preco", "final_esperado", "desconto_esperado"),
        [
            (0, 0, 0),
            (1, 0, 1),
            (100, 0, 100),
            (499, 0, 499),
            (500, 0, 500),
            (501, 1, 500),
            (502, 2, 500),
            (1000, 500, 500),
            (2500, 2000, 500),
        ],
    )
    def test_calculo_fixo500_com_piso_zero(
        self, preco, final_esperado, desconto_esperado
    ):
        resultado = aplicar_desconto(preco, "FIXO500", "2022-03-15")
        assert resultado == {
            "preco_final": final_esperado,
            "desconto": desconto_esperado,
            "cupom_aplicado": "FIXO500",
        }


class TestCupomBemvindo:
    @pytest.mark.parametrize(
        "data_na_janela",
        [
            "2024-01-01",
            "2024-01-02",
            "2024-02-29",
            "2024-06-15",
            "2024-12-30",
            "2024-12-31",
        ],
    )
    @pytest.mark.parametrize(
        ("preco", "final_esperado", "desconto_esperado"),
        [
            (0, 0, 0),
            (1, 0, 1),
            (4, 3, 1),
            (5, 4, 1),
            (6, 4, 2),
            (99, 79, 20),
            (100, 80, 20),
            (101, 80, 21),
            (1000, 800, 200),
        ],
    )
    def test_bemvindo_dentro_da_janela_2024(
        self, data_na_janela, preco, final_esperado, desconto_esperado
    ):
        resultado = aplicar_desconto(preco, "BEMVINDO", data_na_janela)
        assert resultado == {
            "preco_final": final_esperado,
            "desconto": desconto_esperado,
            "cupom_aplicado": "BEMVINDO",
        }

    @pytest.mark.parametrize(
        "data_fora_da_janela",
        [
            "0001-01-01",
            "2023-01-01",
            "2023-06-15",
            "2023-12-30",
            "2023-12-31",
            "2025-01-01",
            "2025-01-02",
            "2025-06-15",
            "2025-12-31",
            "9999-12-31",
        ],
    )
    @pytest.mark.parametrize("preco", [0, 1, 100, 101, 1000])
    def test_bemvindo_fora_da_janela_nao_aplica(self, data_fora_da_janela, preco):
        resultado = aplicar_desconto(preco, "BEMVINDO", data_fora_da_janela)
        assert resultado == {
            "preco_final": preco,
            "desconto": 0,
            "cupom_aplicado": None,
        }


class TestCupomNatal:
    @pytest.mark.parametrize(
        "data_natal",
        [
            "0001-12-24",
            "0001-12-25",
            "1999-12-24",
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
        ("preco", "final_esperado", "desconto_esperado"),
        [
            (0, 0, 0),
            (1, 0, 1),
            (6, 5, 1),
            (7, 5, 2),
            (19, 16, 3),
            (20, 17, 3),
            (21, 17, 4),
            (99, 84, 15),
            (100, 85, 15),
            (101, 85, 16),
            (200, 170, 30),
            (1000, 850, 150),
        ],
    )
    def test_natal_em_24_e_25_de_dezembro(
        self, data_natal, preco, final_esperado, desconto_esperado
    ):
        resultado = aplicar_desconto(preco, "NATAL", data_natal)
        assert resultado == {
            "preco_final": final_esperado,
            "desconto": desconto_esperado,
            "cupom_aplicado": "NATAL",
        }

    @pytest.mark.parametrize(
        "data_nao_natal",
        [
            "2024-12-23",
            "2024-12-26",
            "2024-12-01",
            "2024-12-12",
            "2024-12-31",
            "2024-11-24",
            "2024-11-25",
            "2024-01-24",
            "2024-01-25",
            "2023-12-23",
            "2023-12-26",
            "0001-12-23",
            "9999-12-26",
        ],
    )
    @pytest.mark.parametrize("preco", [0, 1, 100, 101, 1000])
    def test_natal_fora_das_datas_nao_aplica(self, data_nao_natal, preco):
        resultado = aplicar_desconto(preco, "NATAL", data_nao_natal)
        assert resultado == {
            "preco_final": preco,
            "desconto": 0,
            "cupom_aplicado": None,
        }
