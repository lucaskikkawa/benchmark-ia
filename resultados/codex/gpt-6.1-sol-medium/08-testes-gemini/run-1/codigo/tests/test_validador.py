"""Testes do contrato público, sem dependência do texto dos erros."""
import string

import pytest

from validador import CARACTERES_ESPECIAIS_PERMITIDOS, ValidadorSenha


ESPECIAIS = "!@#$%^&*()-_+="


def conferir(validador, senha, valida, quantidade_erros=0):
    resultado = validador.validar(senha)
    assert isinstance(resultado, tuple)
    assert len(resultado) == 2
    sucesso, erros = resultado
    assert sucesso is valida
    assert isinstance(erros, list)
    assert len(erros) == quantidade_erros
    assert all(isinstance(erro, str) for erro in erros)


def senha_com_tamanho(tamanho):
    return ("Aa1!" * ((tamanho + 3) // 4))[:tamanho]


def test_conjunto_exato_de_especiais():
    assert CARACTERES_ESPECIAIS_PERMITIDOS == set(ESPECIAIS)


def test_limites_padrao():
    validador = ValidadorSenha()
    assert validador.min_tam == 8
    assert validador.max_tam == 64


@pytest.mark.parametrize("tamanho,valida", [(7, False), (8, True), (9, True),
                                                   (63, True), (64, True), (65, False)])
def test_fronteiras_de_tamanho_padrao(tamanho, valida):
    conferir(ValidadorSenha(), senha_com_tamanho(tamanho), valida, 0 if valida else 1)


@pytest.mark.parametrize("minimo,maximo", [(4, 6), (10, 15), (70, 80), (8, 8)])
def test_limites_personalizados(minimo, maximo):
    validador = ValidadorSenha(min_tam=minimo, max_tam=maximo)
    assert (validador.min_tam, validador.max_tam) == (minimo, maximo)
    for tamanho in {minimo - 1, minimo, maximo, maximo + 1}:
        valida = minimo <= tamanho <= maximo
        # O menor caso tem três caracteres e também não contém especial.
        faltas = int(tamanho < minimo) + int(tamanho > maximo) + int(tamanho < 4)
        conferir(validador, senha_com_tamanho(tamanho), valida, faltas)


def test_argumentos_posicionais():
    conferir(ValidadorSenha(4, 4), "Aa1!", True)
    conferir(ValidadorSenha(4, 4), "Aa1!b", False, 1)


@pytest.mark.parametrize("senha", ["abcd1!ef", "ABCD1!EF", "Abcdef!g", "Abcdef12"])
def test_ausencia_de_cada_categoria(senha):
    conferir(ValidadorSenha(), senha, False, 1)
    assert ValidadorSenha().calcular_forca(senha) == "invalida"


@pytest.mark.parametrize("especial", list(ESPECIAIS))
def test_cada_especial_permitido(especial):
    conferir(ValidadorSenha(), "Abcdef1" + especial, True)


@pytest.mark.parametrize("pontuacao", sorted(set(string.punctuation) - set(ESPECIAIS)) + ["€", "🙂"])
def test_pontuacao_fora_do_conjunto_nao_substitui_especial(pontuacao):
    conferir(ValidadorSenha(), "Abcdef1" + pontuacao, False, 1)
    # Não há proibição geral de pontuação extra quando existe um especial válido.
    conferir(ValidadorSenha(), "Abcde1!" + pontuacao, True)


@pytest.mark.parametrize("branco", [" ", "\t", "\n", "\r", "\v", "\f", "\u00a0", "\u2003", "\u2028", "\u3000"])
@pytest.mark.parametrize("posicao", [0, 4, 8])
def test_espacos_em_branco_em_qualquer_posicao(branco, posicao):
    senha = "Abcdef1!"
    senha = senha[:posicao] + branco + senha[posicao:]
    conferir(ValidadorSenha(), senha, False, 1)
    assert ValidadorSenha().calcular_forca(senha) == "invalida"


@pytest.mark.parametrize("repetido", ["a", "A", "1", "!", "é"])
@pytest.mark.parametrize("posicao", range(9))
def test_tres_repetidos_em_todas_as_posicoes(repetido, posicao):
    base = "Bcde2@fg"
    senha = base[:posicao] + repetido * 3 + base[posicao:]
    conferir(ValidadorSenha(), senha, False, 1)


@pytest.mark.parametrize("senha", ["aaBcde1!", "Abcde1!!", "Ab11cde!", "Abc!abab1", "Aa1!aaaa", "aaaB1!bbb"])
def test_repeticoes_duplas_separadas_e_multiplas_triplas(senha):
    invalida = senha in {"Aa1!aaaa", "aaaB1!bbb"}
    conferir(ValidadorSenha(), senha, not invalida, int(invalida))


@pytest.mark.parametrize("senha", ["Ébcdef1!", "Aé12345!", "Abcdef١!", "Abcdef²!"])
def test_categorias_seguem_metodos_unicode_de_str(senha):
    conferir(ValidadorSenha(), senha, True)


@pytest.mark.parametrize("senha,quantidade", [("", 5), ("abc", 4), ("aaa", 5), (" " * 8, 6), ("a" * 65, 5)])
def test_acumula_todas_as_violacoes(senha, quantidade):
    conferir(ValidadorSenha(), senha, False, quantidade)
    assert ValidadorSenha().calcular_forca(senha) == "invalida"


@pytest.mark.parametrize("tamanho,forca", [(8, "fraca"), (9, "fraca"), (10, "media"),
                                         (11, "media"), (13, "media"), (14, "forte"),
                                         (15, "forte"), (64, "forte")])
def test_fronteiras_de_forca(tamanho, forca):
    assert ValidadorSenha().calcular_forca(senha_com_tamanho(tamanho)) == forca


@pytest.mark.parametrize("tamanho", [7, 8, 9, 10, 13, 14, 64, 65])
def test_forca_invalida_independe_do_tamanho(tamanho):
    senha = ("Abcd" * ((tamanho + 3) // 4))[:tamanho]
    assert ValidadorSenha().calcular_forca(senha) == "invalida"


def test_forca_respeita_politica_personalizada():
    assert ValidadorSenha(4, 6).calcular_forca("Aa1!") == "fraca"
    assert ValidadorSenha(12, 20).calcular_forca(senha_com_tamanho(10)) == "invalida"
    assert ValidadorSenha(4, 12).calcular_forca(senha_com_tamanho(14)) == "invalida"
    assert ValidadorSenha(4, 80).calcular_forca(senha_com_tamanho(70)) == "forte"


def test_chamadas_nao_compartilham_erros():
    validador = ValidadorSenha()
    conferir(validador, "", False, 5)
    conferir(validador, "Abcdef1!", True)
    conferir(validador, "Abcdef12", False, 1)
    conferir(validador, "Abcdef1!", True)
