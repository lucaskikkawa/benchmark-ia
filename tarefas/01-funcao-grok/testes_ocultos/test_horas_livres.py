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
    with pytest.raises(TypeError):
        horas_livres((("09:00", "10:00"),), "09:00", "12:00")
    with pytest.raises(TypeError):
        horas_livres((x for x in [("09:00", "10:00")]), "09:00", "12:00")
    with pytest.raises(TypeError):
        horas_livres([b"09:00", b"10:00"], "09:00", "12:00")


def test_digitos_ascii_e_separador():
    for texto in (
        "０９:００",
        "09:０0",
        "09：00",
        "⁹9:00",
        "+9:00",
        "09:00\n",
        "24:00 ",
        "00:00\t",
    ):
        with pytest.raises(ValueError):
            horas_livres([], texto, "12:00")
    with pytest.raises(ValueError):
        horas_livres([], "09:00", "１２:００")
    with pytest.raises(ValueError):
        horas_livres([("０８:００", "09:30")], "09:00", "12:00")


def test_invalido_nao_e_ignorado_fora_ou_zerado():
    with pytest.raises(ValueError):
        horas_livres([("24:99", "24:99")], "09:00", "10:00")
    with pytest.raises(ValueError):
        horas_livres([("25:00", "26:00")], "09:00", "10:00")
    with pytest.raises(ValueError):
        horas_livres([("18:00", "17:00")], "09:00", "10:00")
    with pytest.raises(ValueError):
        horas_livres([("09:00", "10:00"), ("99:00", "99:00")], "08:00", "11:00")
    assert horas_livres([("01:00", "01:00"), ("18:00", "19:00")], "09:00", "12:00") == [
        ("09:00", "12:00")
    ]


def test_fusao_depois_do_recorte_e_transitiva():
    assert horas_livres(
        [("08:00", "11:00"), ("11:00", "13:00")],
        "10:00",
        "14:00",
    ) == [("13:00", "14:00")]
    assert horas_livres(
        [("09:00", "10:00"), ("09:30", "12:00"), ("12:00", "12:30")],
        "08:00",
        "13:00",
    ) == [("08:00", "09:00"), ("12:30", "13:00")]
    assert horas_livres(
        [("10:00", "11:00")] * 30 + [("09:00", "10:00"), ("11:00", "11:00")],
        "09:00",
        "12:00",
    ) == [("11:00", "12:00")]


def test_24_nao_vira_meia_noite():
    assert horas_livres([("22:30", "23:00")], "22:00", "24:00") == [
        ("22:00", "22:30"),
        ("23:00", "24:00"),
    ]
    assert horas_livres([], "00:00", "24:00") == [("00:00", "24:00")]


def test_nao_muta_listas_internas():
    par = ["10:00", "11:00"]
    ocupados = [par, ("12:00", "12:30")]
    copia_par = list(par)
    assert horas_livres(ocupados, "09:00", "13:00") == [
        ("09:00", "10:00"),
        ("11:00", "12:00"),
        ("12:30", "13:00"),
    ]
    assert par == copia_par
    assert ocupados[0] is par


def _minutos(texto):
    hora = int(texto[:2])
    minuto = int(texto[3:])
    if (hora, minuto) == (24, 0):
        return 1440
    return hora * 60 + minuto


def _fmt(total):
    hora, minuto = divmod(total, 60)
    return f"{hora:02d}:{minuto:02d}"


def _grade(ocupados, inicio, fim):
    a = _minutos(inicio)
    b = _minutos(fim)
    ocupado = [False] * 1440
    for ini, end in ocupados:
        x, y = _minutos(ini), _minutos(end)
        if x == y:
            continue
        x = max(x, a)
        y = min(y, b)
        for instante in range(x, y):
            ocupado[instante] = True
    livres = []
    cursor = a
    while cursor < b:
        if ocupado[cursor]:
            cursor += 1
            continue
        fim_livre = cursor
        while fim_livre < b and not ocupado[fim_livre]:
            fim_livre += 1
        livres.append((_fmt(cursor), _fmt(fim_livre)))
        cursor = fim_livre
    return livres


def test_grade_de_um_minuto_no_dia_inteiro():
    ocupados = [( _fmt(minuto), _fmt(minuto + 1)) for minuto in range(0, 1440, 2)]
    assert horas_livres(ocupados, "00:00", "24:00") == _grade(
        ocupados, "00:00", "24:00"
    )
    assert horas_livres(ocupados, "00:00", "24:00")[-1] == ("23:59", "24:00")


def test_amostra_aleatoria_confere_com_grade():
    import random

    gerador = random.Random(0)
    for _ in range(25):
        n = gerador.randint(0, 40)
        ocupados = []
        for _item in range(n):
            a = gerador.randint(0, 1440)
            b = gerador.randint(a, 1440)
            ocupados.append((_fmt(a), _fmt(b)))
        inicio = gerador.randint(0, 1439)
        fim = gerador.randint(inicio + 1, 1440)
        janela = (_fmt(inicio), _fmt(fim))
        assert horas_livres(ocupados, janela[0], janela[1]) == _grade(
            ocupados, janela[0], janela[1]
        )
