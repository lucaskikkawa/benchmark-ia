import pytest

from boletim import fechar_boletim

CHAVES = {"media", "conceito", "aprovado", "descartada"}


def _assert_boletim(provas, media, conceito, aprovado, descartada):
    original = list(provas)
    resultado = fechar_boletim(provas)
    assert provas == original
    assert set(resultado) == CHAVES
    assert isinstance(resultado["media"], float)
    assert resultado["media"] == media
    assert resultado["conceito"] == conceito
    assert resultado["aprovado"] is aprovado
    if descartada is None:
        assert resultado["descartada"] is None
    else:
        assert isinstance(resultado["descartada"], float)
        assert resultado["descartada"] == descartada


def test_conceitos_nas_fronteiras():
    _assert_boletim([9], 9.0, "A", True, None)
    _assert_boletim([7], 7.0, "B", True, None)
    _assert_boletim([5], 5.0, "C", True, None)
    _assert_boletim([4], 4.0, "D", False, None)
    _assert_boletim([0], 0.0, "D", False, None)


def test_nota_dez_e_valida():
    _assert_boletim([10], 10.0, "A", True, None)
    _assert_boletim([10.0], 10.0, "A", True, None)
    _assert_boletim([10, 0, 10, 10], 10.0, "A", True, 0.0)


def test_arredondamento_half_up():
    _assert_boletim([1.005], 1.01, "D", False, None)
    _assert_boletim([4.999], 5.0, "C", True, None)
    _assert_boletim([6.666], 6.67, "C", True, None)
    _assert_boletim([1.0, 1.01], 1.01, "D", False, None)


def test_nao_descarta_com_menos_de_quatro_notas():
    _assert_boletim([1, 2, 3], 2.0, "D", False, None)
    _assert_boletim([0, 0, 1], 0.33, "D", False, None)
    _assert_boletim([None, 8, 8], 8.0, "B", True, None)
    _assert_boletim([None, 1, 2, 3], 2.0, "D", False, None)


def test_descarta_uma_menor_somente_com_quatro_validas():
    _assert_boletim([1, 2, 3, 4], 3.0, "D", False, 1.0)
    _assert_boletim([8, 8, 7, 7], 7.67, "B", True, 7.0)
    _assert_boletim([9, 0, 9, 9], 9.0, "A", True, 0.0)


def test_ausencia_nao_vira_zero():
    _assert_boletim([None, 8], 8.0, "B", True, None)
    _assert_boletim([None, None, None, 6], 6.0, "C", True, None)


def test_lista_vazia_e_so_ausencias():
    with pytest.raises(ValueError):
        fechar_boletim([])
    with pytest.raises(ValueError):
        fechar_boletim([None, None])
    with pytest.raises(ValueError):
        fechar_boletim([None])


def test_mais_de_quatro_posicoes():
    with pytest.raises(ValueError):
        fechar_boletim([1, 1, 1, 1, 1])
    with pytest.raises(ValueError):
        fechar_boletim([1, None, None, None, None])


def test_notas_fora_do_intervalo():
    with pytest.raises(ValueError):
        fechar_boletim([-0.1])
    with pytest.raises(ValueError):
        fechar_boletim([10.001])
    with pytest.raises(ValueError):
        fechar_boletim([float("nan")])
    with pytest.raises(ValueError):
        fechar_boletim([float("inf")])


def test_tipos_invalidos():
    with pytest.raises(TypeError):
        fechar_boletim([True])
    with pytest.raises(TypeError):
        fechar_boletim([False])
    with pytest.raises(TypeError):
        fechar_boletim(["7"])
    with pytest.raises(TypeError):
        fechar_boletim((7, 8))
    with pytest.raises(TypeError):
        fechar_boletim(None)


def test_nao_muta_a_entrada():
    provas = [None, 10, 1, 2]
    copia = list(provas)
    fechar_boletim(provas)
    assert provas == copia
