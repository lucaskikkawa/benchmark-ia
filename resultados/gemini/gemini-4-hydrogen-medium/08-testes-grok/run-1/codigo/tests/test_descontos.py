import datetime
import pytest

from descontos import aplicar_desconto


def _assert_resultado(res, preco_centavos, preco_final, cupom_aplicado):
    assert isinstance(res, dict)
    assert set(res.keys()) == {"preco_final", "desconto", "cupom_aplicado"}
    assert type(res["preco_final"]) is int
    assert type(res["desconto"]) is int
    assert res["preco_final"] == preco_final
    assert res["desconto"] == preco_centavos - preco_final
    assert res["cupom_aplicado"] == cupom_aplicado


class TestEstruturaETipos:
    @pytest.mark.parametrize("preco_invalido", [True, False, 100.0, 0.0, "100", None, [100]])
    def test_preco_tipo_invalido(self, preco_invalido):
        with pytest.raises(TypeError):
            aplicar_desconto(preco_invalido, None, "2024-06-15")

    @pytest.mark.parametrize("preco_negativo", [-1, -100, -500])
    def test_preco_negativo(self, preco_negativo):
        with pytest.raises(ValueError):
            aplicar_desconto(preco_negativo, None, "2024-06-15")

    @pytest.mark.parametrize("cupom_invalido", [123, 0, True, False, 10.5, ["OFF10"], b"OFF10"])
    def test_cupom_tipo_invalido(self, cupom_invalido):
        with pytest.raises(TypeError):
            aplicar_desconto(1000, cupom_invalido, "2024-06-15")

    @pytest.mark.parametrize(
        "hoje_invalido",
        [datetime.date(2024, 6, 15), None, 20240615, True, ["2024-06-15"]],
    )
    def test_hoje_tipo_invalido(self, hoje_invalido):
        with pytest.raises(TypeError):
            aplicar_desconto(1000, None, hoje_invalido)


class TestValidacaoData:
    @pytest.mark.parametrize(
        "data_invalida",
        [
            "",
            "2024-1-1",
            "2024-01-1",
            "2024-1-01",
            "20240101",
            "2024/01/01",
            "01-01-2024",
            "24-01-01",
            " 2024-01-01",
            "2024-01-01 ",
            "2024-01-01T00:00:00",
            "2024-0a-01",
            "0000-01-01",
            "2024-00-01",
            "2024-13-01",
            "2024-01-00",
            "2024-01-32",
            "2024-04-31",
            "2023-02-29",
            "1900-02-29",
            "2100-02-29",
        ],
    )
    def test_datas_invalidas(self, data_invalida):
        with pytest.raises(ValueError):
            aplicar_desconto(1000, None, data_invalida)

    @pytest.mark.parametrize(
        "data_valida",
        [
            "0001-01-01",
            "0001-12-25",
            "2000-02-29",
            "2024-02-29",
            "9999-12-31",
        ],
    )
    def test_datas_validas_limites_e_bissextos(self, data_valida):
        res = aplicar_desconto(1000, None, data_valida)
        _assert_resultado(res, 1000, 1000, None)


class TestCupomVazioEDesconhecido:
    @pytest.mark.parametrize("cupom", [None, ""])
    @pytest.mark.parametrize("preco", [0, 1, 1000])
    def test_sem_cupom_ou_vazio(self, cupom, preco):
        res = aplicar_desconto(preco, cupom, "2024-06-15")
        _assert_resultado(res, preco, preco, None)

    @pytest.mark.parametrize(
        "cupom_desconhecido",
        [
            " ",
            "\t",
            "\n",
            " OFF10",
            "OFF10 ",
            "off10",
            "off5",
            "fixo500",
            "bemvindo",
            "natal",
            "OFF20",
            "DESCONTO",
            "NATAL2024",
        ],
    )
    def test_cupom_desconhecido_levanta_value_error(self, cupom_desconhecido):
        with pytest.raises(ValueError):
            aplicar_desconto(1000, cupom_desconhecido, "2024-06-15")


class TestCuponsPercentuais:
    @pytest.mark.parametrize(
        ("preco", "esperado"),
        [
            (0, 0),
            (1, 0),
            (5, 4),
            (9, 8),
            (10, 9),
            (12, 10),
            (15, 13),
            (19, 17),
            (99, 89),
            (100, 90),
            (1000, 900),
        ],
    )
    def test_off10(self, preco, esperado):
        res = aplicar_desconto(preco, "OFF10", "2023-05-10")
        _assert_resultado(res, preco, esperado, "OFF10")

    @pytest.mark.parametrize(
        ("preco", "esperado"),
        [
            (0, 0),
            (1, 0),
            (18, 17),
            (19, 18),
            (20, 19),
            (100, 95),
            (101, 95),
            (200, 190),
        ],
    )
    def test_off5(self, preco, esperado):
        res = aplicar_desconto(preco, "OFF5", "2023-05-10")
        _assert_resultado(res, preco, esperado, "OFF5")


class TestCupomFixo500:
    @pytest.mark.parametrize(
        ("preco", "esperado"),
        [
            (0, 0),
            (1, 0),
            (100, 0),
            (499, 0),
            (500, 0),
            (501, 1),
            (1234, 734),
        ],
    )
    def test_fixo500(self, preco, esperado):
        res = aplicar_desconto(preco, "FIXO500", "2023-05-10")
        _assert_resultado(res, preco, esperado, "FIXO500")


class TestCupomBemvindo:
    @pytest.mark.parametrize("hoje", ["2024-01-01", "2024-06-15", "2024-12-31"])
    @pytest.mark.parametrize(
        ("preco", "esperado"),
        [
            (0, 0),
            (1, 0),
            (2, 1),
            (4, 3),
            (5, 4),
            (100, 80),
            (101, 80),
        ],
    )
    def test_bemvindo_dentro_da_janela(self, hoje, preco, esperado):
        res = aplicar_desconto(preco, "BEMVINDO", hoje)
        _assert_resultado(res, preco, esperado, "BEMVINDO")

    @pytest.mark.parametrize(
        "hoje",
        ["2023-12-31", "2025-01-01", "2023-06-15", "2025-06-15", "0001-01-01", "9999-12-31"],
    )
    @pytest.mark.parametrize("preco", [0, 1, 1000])
    def test_bemvindo_fora_da_janela(self, hoje, preco):
        res = aplicar_desconto(preco, "BEMVINDO", hoje)
        _assert_resultado(res, preco, preco, None)


class TestCupomNatal:
    @pytest.mark.parametrize(
        "hoje",
        [
            "0001-12-24",
            "0001-12-25",
            "1999-12-24",
            "2024-12-24",
            "2024-12-25",
            "2025-12-25",
            "9999-12-24",
            "9999-12-25",
        ],
    )
    @pytest.mark.parametrize(
        ("preco", "esperado"),
        [
            (0, 0),
            (1, 0),
            (2, 1),
            (100, 85),
            (101, 85),
            (200, 170),
        ],
    )
    def test_natal_valido(self, hoje, preco, esperado):
        res = aplicar_desconto(preco, "NATAL", hoje)
        _assert_resultado(res, preco, esperado, "NATAL")

    @pytest.mark.parametrize(
        "hoje",
        [
            "2024-12-23",
            "2024-12-26",
            "2024-11-25",
            "2024-01-24",
            "2024-06-15",
        ],
    )
    @pytest.mark.parametrize("preco", [0, 1, 1000])
    def test_natal_fora_da_data(self, hoje, preco):
        res = aplicar_desconto(preco, "NATAL", hoje)
        _assert_resultado(res, preco, preco, None)
