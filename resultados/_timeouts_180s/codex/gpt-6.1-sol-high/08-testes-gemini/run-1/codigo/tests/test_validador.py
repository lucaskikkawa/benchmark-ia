"""Testes do contrato público, sem depender do texto ou da ordem dos erros."""

import pytest

from validador import CARACTERES_ESPECIAIS_PERMITIDOS, ValidadorSenha


def senha_com_tamanho(tamanho):
    """Contém as quatro categorias a partir de 4 caracteres, sem trincas."""
    return ("Aa1!" + "bC2@" * ((tamanho + 3) // 4))[:tamanho]


def conferir_resultado(validador, senha, esperada, quantidade_erros=None):
    resultado = validador.validar(senha)
    assert isinstance(resultado, tuple)
    assert len(resultado) == 2
    valida, erros = resultado
    assert valida is esperada
    assert isinstance(erros, list)
    assert all(isinstance(erro, str) for erro in erros)
    if esperada:
        assert erros == []
    else:
        assert erros
    if quantidade_erros is not None:
        assert len(erros) == quantidade_erros


def test_constante_de_especiais():
    assert CARACTERES_ESPECIAIS_PERMITIDOS == set("!@#$%^&*()-_+=")


def test_limites_padrao():
    validador = ValidadorSenha()
    assert validador.min_tam == 8
    assert validador.max_tam == 64


@pytest.mark.parametrize("tamanho", range(8, 65))
def test_todos_os_tamanhos_validos_padrao(tamanho):
    conferir_resultado(ValidadorSenha(), senha_com_tamanho(tamanho), True)


@pytest.mark.parametrize("tamanho", [4, 5, 6, 7, 65, 66, 100])
def test_tamanho_invalido_com_demais_regras_satisfeitas(tamanho):
    conferir_resultado(
        ValidadorSenha(), senha_com_tamanho(tamanho), False, quantidade_erros=1
    )


@pytest.mark.parametrize("minimo,maximo", [(4, 4), (5, 7), (10, 14), (65, 70)])
def test_parametros_do_construtor_e_limites_inclusivos(minimo, maximo):
    validador = ValidadorSenha(min_tam=minimo, max_tam=maximo)
    assert validador.min_tam == minimo
    assert validador.max_tam == maximo
    conferir_resultado(validador, senha_com_tamanho(minimo), True)
    conferir_resultado(validador, senha_com_tamanho(maximo), True)
    conferir_resultado(validador, senha_com_tamanho(minimo - 1), False)
    conferir_resultado(validador, senha_com_tamanho(maximo + 1), False, 1)


def test_parametros_posicionais_e_instancias_independentes():
    curta = ValidadorSenha(4, 6)
    longa = ValidadorSenha(10, 80)
    conferir_resultado(curta, "Aa1!", True)
    conferir_resultado(longa, "Aa1!", False, 1)
    conferir_resultado(longa, senha_com_tamanho(80), True)
    conferir_resultado(curta, senha_com_tamanho(80), False, 1)
    conferir_resultado(curta, "Aa1!", True)


@pytest.mark.parametrize(
    "senha",
    [
        "ab1!cd2@",  # falta maiúscula
        "AB1!CD2@",  # falta minúscula
        "Abc!Def@",  # falta dígito
        "Ab12Cd34",  # falta especial permitido
    ],
)
def test_cada_categoria_e_obrigatoria(senha):
    conferir_resultado(ValidadorSenha(), senha, False, 1)
    assert ValidadorSenha().calcular_forca(senha) == "invalida"


@pytest.mark.parametrize("especial", list("!@#$%^&*()-_+="))
def test_cada_especial_permitido_e_suficiente(especial):
    conferir_resultado(ValidadorSenha(), "Ab12Cd3" + especial, True)


@pytest.mark.parametrize("pontuacao", list(".,:;?/\\|[]{}<>`~\"'") + ["©", "🙂"])
def test_outros_simbolos_nao_substituem_especial_permitido(pontuacao):
    conferir_resultado(ValidadorSenha(), "Ab12Cd3" + pontuacao, False, 1)


@pytest.mark.parametrize("extra", ["?", "/", "[", "🙂", "\u200b"])
def test_simbolos_extras_nao_sao_proibidos_se_ha_especial_permitido(extra):
    conferir_resultado(ValidadorSenha(), "Ab12Cd3!" + extra, True)


@pytest.mark.parametrize(
    "espaco", [" ", "\t", "\n", "\r", "\v", "\f", "\u00a0", "\u2003", "\u2028", "\u3000"]
)
@pytest.mark.parametrize("posicao", [0, 4, 8])
def test_espacos_em_branco_em_qualquer_posicao(espaco, posicao):
    base = "Ab12Cd3!"
    senha = base[:posicao] + espaco + base[posicao:]
    conferir_resultado(ValidadorSenha(), senha, False, 1)
    assert ValidadorSenha().calcular_forca(senha) == "invalida"


@pytest.mark.parametrize("caractere", ["a", "A", "1", "!", "é", "🙂"])
@pytest.mark.parametrize("posicao", [0, 4, 8])
def test_trincas_inclusive_no_inicio_e_no_final(caractere, posicao):
    base = "Ab12Cd3!"
    senha = base[:posicao] + caractere * 3 + base[posicao:]
    conferir_resultado(ValidadorSenha(), senha, False, 1)
    assert ValidadorSenha().calcular_forca(senha) == "invalida"


@pytest.mark.parametrize(
    "senha",
    ["Aa1!bbCd", "bbAa1!Cd", "Aa1!Cdbb", "AAaa11!!", "Aa1!abababa", "Aa1!aaaa"],
)
def test_duplas_e_repeticoes_nao_consecutivas(senha):
    # O último exemplo contém uma sequência maior que três, também proibida.
    conferir_resultado(ValidadorSenha(), senha, senha != "Aa1!aaaa")


@pytest.mark.parametrize("senha", ["Éa1!bcde", "Aé1!bcde", "Aa١!bcde", "Aa²!bcde"])
def test_categorias_unicode_seguem_metodos_de_str(senha):
    conferir_resultado(ValidadorSenha(), senha, True)


@pytest.mark.parametrize(
    "senha,quantidade",
    [("", 5), (" ", 6), ("aaa", 5), (" " * 65, 7), ("aaa " * 17, 6)],
)
def test_acumula_todas_as_regras_violadas(senha, quantidade):
    conferir_resultado(ValidadorSenha(), senha, False, quantidade)


def test_chamadas_sucessivas_nao_acumulam_estado():
    validador = ValidadorSenha()
    _, erros_anteriores = validador.validar("")
    copia = erros_anteriores.copy()
    conferir_resultado(validador, "Ab12Cd3!", True)
    conferir_resultado(validador, "Ab12Cd34", False, 1)
    conferir_resultado(validador, "Ab12Cd3!", True)
    assert erros_anteriores == copia


@pytest.mark.parametrize(
    "tamanho,forca",
    [(8, "fraca"), (9, "fraca"), (10, "media"), (11, "media"),
     (12, "media"), (13, "media"), (14, "forte"), (15, "forte"), (64, "forte")],
)
def test_faixas_de_forca_e_fronteiras(tamanho, forca):
    assert ValidadorSenha().calcular_forca(senha_com_tamanho(tamanho)) == forca


@pytest.mark.parametrize(
    "senha", ["", "Aa1!bcD", senha_com_tamanho(65), "abcdefghij", "Ab1!bcDefaaa"]
)
def test_forca_invalida_tem_precedencia_sobre_tamanho(senha):
    assert ValidadorSenha().calcular_forca(senha) == "invalida"


@pytest.mark.parametrize(
    "minimo,maximo,tamanho,forca",
    [(4, 100, 4, "fraca"), (4, 100, 65, "forte"),
     (10, 64, 9, "invalida"), (4, 9, 10, "invalida"),
     (14, 20, 13, "invalida"), (14, 20, 14, "forte")],
)
def test_forca_respeita_politica_configurada(minimo, maximo, tamanho, forca):
    validador = ValidadorSenha(minimo, maximo)
    assert validador.calcular_forca(senha_com_tamanho(tamanho)) == forca
