import pytest

from validador import CARACTERES_ESPECIAIS_PERMITIDOS, ValidadorSenha


def assert_valida(validador, senha):
    valida, erros = validador.validar(senha)
    assert valida is True
    assert erros == []


def assert_invalida(validador, senha):
    valida, erros = validador.validar(senha)
    assert valida is False
    assert erros


def test_senha_que_cumpre_todas_as_regras():
    assert_valida(ValidadorSenha(), "Abcdef1!")


def test_limite_minimo_padrao_e_inclusivo():
    assert_valida(ValidadorSenha(), "Abcdef1!")


def test_um_abaixo_do_minimo_e_invalido():
    assert_invalida(ValidadorSenha(), "Abcde1!")


def test_limite_maximo_padrao_e_inclusivo():
    validador = ValidadorSenha()
    assert_valida(validador, "A" + "b" * 61 + "1!")
    assert_invalida(validador, "A" + "b" * 62 + "1!")


def test_limites_personalizados_sao_respeitados():
    validador = ValidadorSenha(min_tam=5, max_tam=12)
    assert_valida(validador, "Ab1!c")
    assert_valida(validador, "Abcdefg1!xyz")
    assert_invalida(validador, "Ab1!")
    assert_invalida(validador, "Abcdefgh1!xyz")


@pytest.mark.parametrize(
    "senha",
    [
        "abcdef1!",  # falta maiúscula
        "ABCDEFG1!",  # falta minúscula
        "Abcdefg!!",  # falta dígito
        "Abcdefg1x",  # falta especial permitido
        "Abcdef1 !",  # espaço comum
        "Abcdef1\t!",  # tabulação
        "Abcdef1\n!",  # quebra de linha
        "Abcdef111!",  # repetição no final
        "Aaa1!xyz",  # repetição no início
        "Abc111!x",  # repetição no meio
    ],
)
def test_rejeita_cada_regra_violada(senha):
    assert_invalida(ValidadorSenha(), senha)


def test_pontuacao_nao_permitida_nao_conta_como_especial():
    assert "?" not in CARACTERES_ESPECIAIS_PERMITIDOS
    assert_invalida(ValidadorSenha(), "Abcdef1?")


def test_todos_os_especiais_permitidos_sao_aceitos():
    validador = ValidadorSenha()
    for especial in CARACTERES_ESPECIAIS_PERMITIDOS:
        assert_valida(validador, "Abcdef1" + especial)


@pytest.mark.parametrize(
    ("senha", "forca"),
    [
        ("Abcdef1!", "fraca"),  # 8
        ("Abcdefg1!", "fraca"),  # 9
        ("Abcdefgh1!x", "media"),  # 11 (válida)
        ("Abcdefgh1!xy", "media"),  # 12
        ("Abcdefgh1!xyz", "media"),  # 13
        ("Abcdefgh1!xyza", "forte"),  # 14
        ("Abcdefgh1!xyzab", "forte"),  # 15
    ],
)
def test_calcular_forca_nos_limites(senha, forca):
    assert ValidadorSenha().calcular_forca(senha) == forca


@pytest.mark.parametrize("senha", ["Abcde1!", "Abcdef111!"])
def test_senha_invalida_tem_forca_invalida(senha):
    assert ValidadorSenha().calcular_forca(senha) == "invalida"
