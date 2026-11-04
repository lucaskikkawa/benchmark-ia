import datetime
import pytest

from descontos import aplicar_desconto


class TestContratoBasicoERetorno:
    def test_chaves_exatas_e_tipos_do_retorno_sem_cupom(self):
        res = aplicar_desconto(1000, None, "2024-05-10")
        assert isinstance(res, dict)
        assert set(res.keys()) == {"preco_final", "desconto", "cupom_aplicado"}
        assert type(res["preco_final"]) is int
        assert type(res["desconto"]) is int
        assert res["cupom_aplicado"] is None
        assert res == {
            "preco_final": 1000,
            "desconto": 0,
            "cupom_aplicado": None,
        }

    def test_chaves_exatas_e_tipos_do_retorno_com_cupom(self):
        res = aplicar_desconto(1000, "OFF10", "2024-05-10")
        assert isinstance(res, dict)
        assert set(res.keys()) == {"preco_final", "desconto", "cupom_aplicado"}
        assert type(res["preco_final"]) is int
        assert type(res["desconto"]) is int
        assert type(res["cupom_aplicado"]) is str
        assert res == {
            "preco_final": 900,
            "desconto": 100,
            "cupom_aplicado": "OFF10",
        }


class TestValidacaoPrecoCentavos:
    @pytest.mark.parametrize(
        "preco_invalido",
        [
            True,
            False,
            0.0,
            100.0,
            99.99,
            -1.5,
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
            aplicar_desconto(preco_invalido, None, "2024-06-01")
        with pytest.raises(TypeError):
            aplicar_desconto(preco_invalido, "OFF10", "2024-06-01")

    @pytest.mark.parametrize("preco_negativo", [-1, -2, -100, -500, -999999])
    def test_preco_negativo_levanta_value_error(self, preco_negativo):
        with pytest.raises(ValueError):
            aplicar_desconto(preco_negativo, None, "2024-06-01")
        with pytest.raises(ValueError):
            aplicar_desconto(preco_negativo, "OFF10", "2024-06-01")
        with pytest.raises(ValueError):
            aplicar_desconto(preco_negativo, "FIXO500", "2024-06-01")

    def test_preco_zero_eh_valido(self):
        res = aplicar_desconto(0, None, "2024-06-01")
        assert res == {"preco_final": 0, "desconto": 0, "cupom_aplicado": None}


class TestValidacaoCupom:
    @pytest.mark.parametrize(
        "cupom_invalido",
        [
            0,
            10,
            10.5,
            True,
            False,
            ["OFF10"],
            ("OFF10",),
            {"cupom": "OFF10"},
            b"OFF10",
        ],
    )
    def test_cupom_tipo_invalido_levanta_type_error(self, cupom_invalido):
        with pytest.raises(TypeError):
            aplicar_desconto(1000, cupom_invalido, "2024-06-01")

    @pytest.mark.parametrize("cupom_vazio", [None, ""])
    @pytest.mark.parametrize("preco", [0, 1, 100, 12345])
    def test_cupom_none_ou_string_vazia_nao_da_desconto(self, cupom_vazio, preco):
        res = aplicar_desconto(preco, cupom_vazio, "2024-06-01")
        assert res == {
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
            " OFF5",
            "OFF5 ",
            "off5",
            " FIXO500",
            "FIXO500 ",
            "fixo500",
            " BEMVINDO",
            "BEMVINDO ",
            "bemvindo",
            " NATAL",
            "NATAL ",
            "natal",
            "OFF20",
            "FIXO100",
            "DESCONTO",
            "NONE",
            "null",
        ],
    )
    def test_cupom_desconhecido_ou_com_espaco_ou_minusculo_levanta_value_error(
        self, cupom_desconhecido
    ):
        with pytest.raises(ValueError):
            aplicar_desconto(1000, cupom_desconhecido, "2024-12-25")


class TestValidacaoDataHoje:
    @pytest.mark.parametrize(
        "hoje_invalido",
        [
            None,
            20240101,
            2024,
            12.34,
            True,
            False,
            datetime.date(2024, 1, 1),
            datetime.datetime(2024, 1, 1, 0, 0),
            ["2024-01-01"],
            b"2024-01-01",
        ],
    )
    def test_hoje_tipo_invalido_levanta_type_error(self, hoje_invalido):
        with pytest.raises(TypeError):
            aplicar_desconto(1000, None, hoje_invalido)
        with pytest.raises(TypeError):
            aplicar_desconto(1000, "OFF10", hoje_invalido)

    @pytest.mark.parametrize(
        "data_invalida",
        [
            "",
            "20240101",
            "2024-W01-1",
            "2024-W01-2",
            "2024/01/01",
            "2024/01-01",
            "2024-01/01",
            "2024.01.01",
            "2024-1-01",
            "2024-01-1",
            "24-01-01",
            "01-01-2024",
            "2024-01-01 ",
            " 2024-01-01",
            "2024-01-01T00:00:00",
            "0000-01-01",
            "0000-12-25",
            "10000-01-01",
            "-001-01-01",
            "+2024-01-01",
            "1900-02-29",
            "2100-02-29",
            "2023-02-29",
            "2025-02-29",
            "2024-02-30",
            "2024-00-10",
            "2024-13-01",
            "2024-01-00",
            "2024-01-32",
            "2024-04-31",
            "2024-06-31",
            "2024-09-31",
            "2024-11-31",
            "abcd-ef-gh",
            "2024-ab-01",
            "2024-01-cd",
        ],
    )
    def test_data_invalida_levanta_value_error(self, data_invalida):
        with pytest.raises(ValueError):
            aplicar_desconto(1000, None, data_invalida)
        with pytest.raises(ValueError):
            aplicar_desconto(1000, "", data_invalida)
        with pytest.raises(ValueError):
            aplicar_desconto(1000, "OFF10", data_invalida)

    @pytest.mark.parametrize(
        "data_valida",
        [
            "2000-02-29",
            "2024-02-29",
            "0004-02-29",
            "0001-01-01",
            "0001-12-25",
            "9999-12-31",
            "9999-12-25",
        ],
    )
    def test_datas_validas_bissextas_e_extremos(self, data_valida):
        res = aplicar_desconto(100, "OFF10", data_valida)
        assert res == {
            "preco_final": 90,
            "desconto": 10,
            "cupom_aplicado": "OFF10",
        }


class TestCupomOFF10:
    @pytest.mark.parametrize(
        "preco,esperado_final,esperado_desconto",
        [
            (0, 0, 0),
            (1, 0, 1),
            (2, 1, 1),
            (9, 8, 1),
            (10, 9, 1),
            (11, 9, 2),
            (19, 17, 2),
            (99, 89, 10),
            (100, 90, 10),
            (101, 90, 11),
            (250, 225, 25),
            (1000, 900, 100),
        ],
    )
    def test_calculo_off10_com_piso(self, preco, esperado_final, esperado_desconto):
        res = aplicar_desconto(preco, "OFF10", "2023-07-15")
        assert res == {
            "preco_final": esperado_final,
            "desconto": esperado_desconto,
            "cupom_aplicado": "OFF10",
        }
        assert res["desconto"] == preco - res["preco_final"]


class TestCupomOFF5:
    @pytest.mark.parametrize(
        "preco,esperado_final,esperado_desconto",
        [
            (0, 0, 0),
            (1, 0, 1),
            (19, 18, 1),
            (20, 19, 1),
            (21, 19, 2),
            (99, 94, 5),
            (100, 95, 5),
            (101, 95, 6),
            (200, 190, 10),
            (1000, 950, 50),
        ],
    )
    def test_calculo_off5_com_piso(self, preco, esperado_final, esperado_desconto):
        res = aplicar_desconto(preco, "OFF5", "2023-07-15")
        assert res == {
            "preco_final": esperado_final,
            "desconto": esperado_desconto,
            "cupom_aplicado": "OFF5",
        }
        assert res["desconto"] == preco - res["preco_final"]


class TestCupomFIXO500:
    @pytest.mark.parametrize(
        "preco,esperado_final,esperado_desconto",
        [
            (0, 0, 0),
            (1, 0, 1),
            (100, 0, 100),
            (250, 0, 250),
            (499, 0, 499),
            (500, 0, 500),
            (501, 1, 500),
            (600, 100, 500),
            (1000, 500, 500),
        ],
    )
    def test_calculo_fixo500_com_piso_zero(
        self, preco, esperado_final, esperado_desconto
    ):
        res = aplicar_desconto(preco, "FIXO500", "2023-07-15")
        assert res == {
            "preco_final": esperado_final,
            "desconto": esperado_desconto,
            "cupom_aplicado": "FIXO500",
        }
        assert res["preco_final"] >= 0
        assert res["desconto"] == preco - res["preco_final"]


class TestCupomBEMVINDO:
    @pytest.mark.parametrize(
        "data_em_2024",
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
        "preco,esperado_final,esperado_desconto",
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
    def test_bemvindo_dentro_da_janela(
        self, data_em_2024, preco, esperado_final, esperado_desconto
    ):
        res = aplicar_desconto(preco, "BEMVINDO", data_em_2024)
        assert res == {
            "preco_final": esperado_final,
            "desconto": esperado_desconto,
            "cupom_aplicado": "BEMVINDO",
        }

    @pytest.mark.parametrize(
        "data_fora_2024",
        [
            "2023-12-31",
            "2023-01-01",
            "2023-06-15",
            "2025-01-01",
            "2025-12-31",
            "2025-06-15",
            "0001-01-01",
            "9999-12-31",
        ],
    )
    @pytest.mark.parametrize("preco", [0, 1, 100, 1000])
    def test_bemvindo_fora_da_janela_nao_aplica(self, data_fora_2024, preco):
        res = aplicar_desconto(preco, "BEMVINDO", data_fora_2024)
        assert res == {
            "preco_final": preco,
            "desconto": 0,
            "cupom_aplicado": None,
        }


class TestCupomNATAL:
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
        "preco,esperado_final,esperado_desconto",
        [
            (0, 0, 0),
            (1, 0, 1),
            (6, 5, 1),
            (7, 5, 2),
            (19, 16, 3),
            (20, 17, 3),
            (21, 17, 4),
            (100, 85, 15),
            (101, 85, 16),
            (200, 170, 30),
            (1000, 850, 150),
        ],
    )
    def test_natal_em_24_e_25_de_dezembro_qualquer_ano(
        self, data_natal, preco, esperado_final, esperado_desconto
    ):
        res = aplicar_desconto(preco, "NATAL", data_natal)
        assert res == {
            "preco_final": esperado_final,
            "desconto": esperado_desconto,
            "cupom_aplicado": "NATAL",
        }

    @pytest.mark.parametrize(
        "data_nao_natal",
        [
            "2024-12-23",
            "2024-12-26",
            "2024-12-01",
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
    @pytest.mark.parametrize("preco", [0, 1, 100, 1000])
    def test_natal_fora_da_janela_nao_aplica(self, data_nao_natal, preco):
        res = aplicar_desconto(preco, "NATAL", data_nao_natal)
        assert res == {
            "preco_final": preco,
            "desconto": 0,
            "cupom_aplicado": None,
        }
