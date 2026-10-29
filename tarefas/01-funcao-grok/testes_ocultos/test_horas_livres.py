import pytest

from solucao import horas_livres


def test_janela_sem_ocupacao():
    assert horas_livres([], "09:00", "12:00") == [("09:00", "12:00")]


def test_janela_totalmente_ocupada():
    assert horas_livres([("09:00", "12:00")], "09:00", "12:00") == []


def test_um_intervalo_no_meio():
    assert horas_livres([("10:00", "11:00")], "09:00", "12:00") == [
        ("09:00", "10:00"),
        ("11:00", "12:00"),
    ]


def test_sobreposicao_e_intervalo_contido():
    assert horas_livres(
        [("10:00", "12:00"), ("11:00", "11:30"), ("09:30", "10:15")],
        "09:00",
        "13:00",
    ) == [("09:00", "09:30"), ("12:00", "13:00")]


def test_adjacentes_se_fundem():
    assert horas_livres(
        [("09:00", "10:00"), ("10:00", "11:00")],
        "09:00",
        "12:00",
    ) == [("11:00", "12:00")]


def test_fora_da_janela_duracao_zero_e_ordem():
    ocupados = [("13:00", "15:00"), ("08:00", "09:30"), ("11:00", "11:00")]
    copia = list(ocupados)
    assert horas_livres(ocupados, "09:00", "12:00") == [("09:30", "12:00")]
    assert ocupados == copia


def test_dia_inteiro_cobre_a_janela():
    assert horas_livres([("00:00", "24:00")], "08:15", "18:45") == []


def test_resolucao_de_um_minuto_e_madrugada():
    assert horas_livres([("09:00", "09:01")], "09:00", "09:02") == [("09:01", "09:02")]
    assert horas_livres([], "00:00", "00:01") == [("00:00", "00:01")]
    assert horas_livres([], "23:59", "24:00") == [("23:59", "24:00")]


def test_fim_do_dia():
    assert horas_livres([("23:30", "24:00")], "23:00", "24:00") == [("23:00", "23:30")]
    assert horas_livres([("24:00", "24:00")], "22:00", "24:00") == [("22:00", "24:00")]


def test_varios_buracos():
    assert horas_livres(
        [("09:15", "09:45"), ("10:00", "10:30"), ("11:00", "11:30")],
        "09:00",
        "12:00",
    ) == [
        ("09:00", "09:15"),
        ("09:45", "10:00"),
        ("10:30", "11:00"),
        ("11:30", "12:00"),
    ]


def test_aceita_lista_no_lugar_de_tupla():
    assert horas_livres([["10:00", "11:00"]], "09:00", "12:00") == [
        ("09:00", "10:00"),
        ("11:00", "12:00"),
    ]


@pytest.mark.parametrize(
    "inicio,fim",
    [
        ("9:00", "12:00"),
        ("09:0", "12:00"),
        ("24:30", "24:40"),
        ("23:60", "23:61"),
        ("ab:cd", "12:00"),
        ("", "12:00"),
        ("09-00", "12:00"),
        ("09:00:00", "12:00"),
        ("09:00 ", "12:00"),
        ("24:00", "24:00"),
        ("12:00", "09:00"),
        ("10:00", "10:00"),
        ("09:00", "24:01"),
    ],
)
def test_janela_invalida(inicio, fim):
    with pytest.raises(ValueError):
        horas_livres([], inicio, fim)


def test_intervalo_ocupado_invertido():
    with pytest.raises(ValueError):
        horas_livres([("12:00", "11:00")], "08:00", "13:00")
    with pytest.raises(ValueError):
        horas_livres([("24:00", "23:00")], "22:00", "24:00")


def test_tipos_invalidos():
    with pytest.raises(TypeError):
        horas_livres(None, "09:00", "10:00")
    with pytest.raises(TypeError):
        horas_livres("09:00", "09:00", "10:00")
    with pytest.raises(TypeError):
        horas_livres([], None, "10:00")
    with pytest.raises(TypeError):
        horas_livres([], "09:00", 1000)
    with pytest.raises(TypeError):
        horas_livres([(9, 10)], "09:00", "10:00")
    with pytest.raises(TypeError):
        horas_livres([("09:00",)], "09:00", "10:00")
    with pytest.raises(TypeError):
        horas_livres([("09:00", "10:00", "11:00")], "09:00", "12:00")
    with pytest.raises(TypeError):
        horas_livres(("09:00", "10:00"), "09:00", "12:00")
