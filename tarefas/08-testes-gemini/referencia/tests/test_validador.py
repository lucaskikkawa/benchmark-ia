import pytest
from validador import ValidadorSenha


@pytest.fixture
def validador():
    return ValidadorSenha()


def test_senha_valida(validador):
    valida, erros = validador.validar("SenhaForte@123")
    assert valida is True
    assert erros == []


def test_min_comprimento(validador):
    # mutante_01
    valida, erros = validador.validar("Ab1!xy")  # 6 caracteres (< 8)
    assert valida is False
    assert any("pelo menos 8 caracteres" in err for err in erros)


def test_max_comprimento(validador):
    # mutante_02
    senha_longa = "A1!" + "a" * 65
    valida, erros = validador.validar(senha_longa)
    assert valida is False
    assert any("no máximo 64 caracteres" in err for err in erros)


def test_requer_maiuscula(validador):
    # mutante_03
    valida, erros = validador.validar("senhafraca@123")
    assert valida is False
    assert any("letra maiúscula" in err for err in erros)


def test_requer_minuscula(validador):
    # mutante_04
    valida, erros = validador.validar("SENHAFORTE@123")
    assert valida is False
    assert any("letra minúscula" in err for err in erros)


def test_requer_digito(validador):
    # mutante_05
    valida, erros = validador.validar("SenhaSemDigito@")
    assert valida is False
    assert any("dígito numérico" in err for err in erros)


def test_requer_caractere_especial(validador):
    # mutante_06
    valida, erros = validador.validar("SenhaSemEspecial123")
    assert valida is False
    assert any("caractere especial permitido" in err for err in erros)


def test_proibe_espacos_em_branco(validador):
    # mutante_07
    valida, erros = validador.validar("Senha Forte @123")
    assert valida is False
    assert any("espaços em branco" in err for err in erros)


def test_proibe_repeticoes_consecutivas(validador):
    # mutante_08
    valida, erros = validador.validar("Senha111@abc")
    assert valida is False
    assert any("3 caracteres repetidos" in err for err in erros)


def test_retorno_booleano_falso_em_caso_de_erro(validador):
    # mutante_09
    valida, erros = validador.validar("invalida")
    assert valida is False
    assert len(erros) > 0


def test_calculo_de_forca(validador):
    # mutante_10
    # Inválida
    assert validador.calcular_forca("fraca") == "invalida"

    # Válida, < 10 chars (tam 8): fraca
    assert validador.calcular_forca("Ab1!xyza") == "fraca"

    # Válida, >= 10 e < 14 chars (tam 11): media
    assert validador.calcular_forca("Ab1!xyzabcd") == "media"

    # Válida, >= 14 chars (tam 15): forte
    assert validador.calcular_forca("Ab1!xyzabcdefgh") == "forte"
