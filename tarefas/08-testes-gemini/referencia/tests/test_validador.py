import pytest
from validador import ValidadorSenha, CARACTERES_ESPECIAIS_PERMITIDOS


@pytest.fixture
def validador():
    return ValidadorSenha()


def test_senha_valida_tamanho_minimo_exato(validador):
    # mutante_01: tamanho 8 exato deve ser válido
    senha_8 = "Ab1!xyzw"  # len == 8
    valida, erros = validador.validar(senha_8)
    assert valida is True
    assert erros == []


def test_senha_tamanho_menor_que_minimo(validador):
    # 7 caracteres (< 8)
    valida, erros = validador.validar("Ab1!xyz")
    assert valida is False
    assert any("pelo menos 8 caracteres" in err for err in erros)


def test_senha_valida_tamanho_maximo_exato(validador):
    # mutante_02: tamanho 64 exato deve ser válido
    senha_64 = "Ab1!" + "abcd" * 15  # len == 64
    valida, erros = validador.validar(senha_64)
    assert valida is True
    assert erros == []


def test_senha_tamanho_maior_que_maximo(validador):
    # 65 caracteres (> 64)
    senha_65 = "Ab1!" + "abcd" * 15 + "e"
    valida, erros = validador.validar(senha_65)
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


def test_requer_caractere_especial_do_conjunto_permitido(validador):
    # mutante_06: caracteres como '.' ou '~' não estão em CARACTERES_ESPECIAIS_PERMITIDOS
    valida, erros = validador.validar("SenhaPonto123.")
    assert valida is False
    assert any("caractere especial permitido" in err for err in erros)

    # Com caractere permitido
    valida_ok, erros_ok = validador.validar("SenhaValida123!")
    assert valida_ok is True
    assert erros_ok == []


def test_proibe_espacos_em_branco_incluindo_tabs_e_newlines(validador):
    # mutante_07: isspace deve pegar tabs e quebras de linha
    valida_tab, erros_tab = validador.validar("Senha\tForte@123")
    assert valida_tab is False
    assert any("espaços em branco" in err for err in erros_tab)

    valida_nl, erros_nl = validador.validar("Senha\nForte@123")
    assert valida_nl is False
    assert any("espaços em branco" in err for err in erros_nl)


def test_proibe_repeticoes_consecutivas_inclusive_no_final(validador):
    # mutante_08: repetição nos últimos caracteres
    valida, erros = validador.validar("SenhaForte@1aaa")
    assert valida is False
    assert any("3 caracteres repetidos" in err for err in erros)


def test_acumula_multiplos_erros_de_validacao(validador):
    # mutante_09: senha sem maiúscula, sem minúscula, sem dígito, sem especial e curta
    valida, erros = validador.validar("...")
    assert valida is False
    assert len(erros) >= 2


def test_calculo_de_forca_limiares_exatos(validador):
    # Inválida
    assert validador.calcular_forca("fraca") == "invalida"

    # Válida, tam 8 (< 10): fraca
    assert validador.calcular_forca("Ab1!xyza") == "fraca"

    # mutante_10: Válida, tam 10 exato (>= 10 e < 14): media
    assert validador.calcular_forca("Ab1!xyzabc") == "media"

    # Válida, tam 13 (< 14): media
    assert validador.calcular_forca("Ab1!xyzabcdef") == "media"

    # mutante_11: Válida, tam 14 exato (>= 14): forte
    assert validador.calcular_forca("Ab1!xyzabcdefg") == "forte"

    # Válida, tam 15 (>= 14): forte
    assert validador.calcular_forca("Ab1!xyzabcdefgh") == "forte"


def test_configuracao_customizada_min_max_tam():
    # mutante_12: construtor respeita limites customizados
    v_custom = ValidadorSenha(min_tam=12, max_tam=20)
    # 10 caracteres é menor que min_tam customizado de 12
    valida, erros = v_custom.validar("Ab1!xyzabc")
    assert valida is False
    assert any("pelo menos 12 caracteres" in err for err in erros)
