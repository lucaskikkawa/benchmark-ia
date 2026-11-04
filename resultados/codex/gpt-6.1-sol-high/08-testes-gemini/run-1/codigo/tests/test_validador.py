"""Testes do contrato público de validação e classificação de senhas."""

import pytest

from validador import CARACTERES_ESPECIAIS_PERMITIDOS, ValidadorSenha


def senha_com_tamanho(tamanho):
    """Senha com todas as categorias e sem espaços ou trincas repetidas."""
    return "Aa1!" + ("bc" * tamanho)[: tamanho - 4]


def conferir_validacao(validador, senha, valida, quantidade_erros=None):
    resultado = validador.validar(senha)
    assert isinstance(resultado, tuple)
    assert len(resultado) == 2
    sucesso, erros = resultado
    assert sucesso is valida
    assert isinstance(erros, list)
    assert all(isinstance(erro, str) for erro in erros)
    if valida:
        assert erros == []
    else:
        assert erros
    if quantidade_erros is not None:
        assert len(erros) == quantidade_erros


def test_conjunto_de_caracteres_especiais():
    assert CARACTERES_ESPECIAIS_PERMITIDOS == set("!@#$%^&*()-_+=")


def test_limites_padrao():
    validador = ValidadorSenha()
    assert validador.min_tam == 8
    assert validador.max_tam == 64


@pytest.mark.parametrize("tamanho,valida", [(7, False), (8, True), (9, True),
                                               (63, True), (64, True), (65, False)])
def test_limites_de_comprimento_padrao(tamanho, valida):
    conferir_validacao(ValidadorSenha(), senha_com_tamanho(tamanho), valida,
                       0 if valida else 1)


@pytest.mark.parametrize("tamanho,valida", [(4, False), (5, True), (6, True),
                                               (7, True), (8, False)])
def test_limites_personalizados(tamanho, valida):
    validador = ValidadorSenha(min_tam=5, max_tam=7)
    assert (validador.min_tam, validador.max_tam) == (5, 7)
    conferir_validacao(validador, senha_com_tamanho(tamanho), valida,
                       0 if valida else 1)


@pytest.mark.parametrize("tamanho,valida", [(4, True), (7, True), (65, True),
                                               (100, True), (101, False)])
def test_limites_personalizados_ampliados(tamanho, valida):
    conferir_validacao(ValidadorSenha(4, 100), senha_com_tamanho(tamanho), valida,
                       0 if valida else 1)


@pytest.mark.parametrize("senha", [
    "abcd12!@",  # Sem maiúscula.
    "ABCD12!@",  # Sem minúscula.
    "Abcdef!@",  # Sem dígito.
    "Abcdef12",  # Sem especial permitido.
])
def test_ausencia_de_cada_categoria(senha):
    conferir_validacao(ValidadorSenha(), senha, False, 1)
    assert ValidadorSenha().calcular_forca(senha) == "invalida"


@pytest.mark.parametrize("especial", list("!@#$%^&*()-_+="))
def test_cada_especial_permitido_satisfaz_a_regra(especial):
    conferir_validacao(ValidadorSenha(), "Abcdef1" + especial, True)


@pytest.mark.parametrize("pontuacao", list(".,:;?/\\|[]{}<>~`\"'"))
def test_outras_pontuacoes_nao_substituem_especial(pontuacao):
    conferir_validacao(ValidadorSenha(), "Abcdef1" + pontuacao, False, 1)


@pytest.mark.parametrize("extra", ["?", ".", "[", "🙂", "\u200b"])
def test_caracteres_adicionais_nao_sao_proibidos(extra):
    conferir_validacao(ValidadorSenha(), "Abcdef1!" + extra, True)


@pytest.mark.parametrize("senha", [
    "Ábcdef1!",  # Maiúscula Unicode.
    "ABCDEFé1!",  # Minúscula Unicode.
    "Abcdef١!",  # Dígito arábico.
    "Abcdef²!",  # isdigit também inclui dígitos sobrescritos.
])
def test_categorias_usam_propriedades_unicode(senha):
    conferir_validacao(ValidadorSenha(), senha, True)


@pytest.mark.parametrize("espaco", [" ", "\t", "\n", "\r", "\v", "\f",
                                       "\u00a0", "\u2003", "\u2028", "\u3000"])
@pytest.mark.parametrize("posicao", [0, 4, 8])
def test_espacos_em_branco_em_qualquer_posicao(espaco, posicao):
    base = "Abcdef1!"
    senha = base[:posicao] + espaco + base[posicao:]
    conferir_validacao(ValidadorSenha(), senha, False, 1)
    assert ValidadorSenha().calcular_forca(senha) == "invalida"


@pytest.mark.parametrize("caractere", ["a", "A", "1", "!", "é", "🙂"])
@pytest.mark.parametrize("posicao", [0, 4, 8])
def test_trinca_repetida_no_inicio_meio_e_final(caractere, posicao):
    base = "Abcdef1!"
    senha = base[:posicao] + caractere * 3 + base[posicao:]
    conferir_validacao(ValidadorSenha(), senha, False, 1)
    assert ValidadorSenha().calcular_forca(senha) == "invalida"


@pytest.mark.parametrize("senha", [
    "aaBcde1!", "Abcde1!aa", "Abc11de!", "Abcde1!!",
    "Aa1!abab", "Aa1!abacada", "Aa1!aAaA",
])
def test_duplas_e_repeticoes_nao_consecutivas_sao_validas(senha):
    conferir_validacao(ValidadorSenha(), senha, True)


@pytest.mark.parametrize("senha,quantidade", [
    ("", 5),
    ("a", 4),
    ("aaa", 5),
    ("A1!", 2),
    ("Abcdefgh", 2),
    (" \t\n", 6),
])
def test_acumula_todas_as_violacoes_sem_depender_das_mensagens(senha, quantidade):
    conferir_validacao(ValidadorSenha(), senha, False, quantidade)
    assert ValidadorSenha().calcular_forca(senha) == "invalida"


@pytest.mark.parametrize("tamanho,forca", [
    (7, "invalida"), (8, "fraca"), (9, "fraca"),
    (10, "media"), (11, "media"), (12, "media"), (13, "media"),
    (14, "forte"), (15, "forte"), (63, "forte"), (64, "forte"),
    (65, "invalida"),
])
def test_faixas_de_forca_e_suas_fronteiras(tamanho, forca):
    assert ValidadorSenha().calcular_forca(senha_com_tamanho(tamanho)) == forca


@pytest.mark.parametrize("senha", [
    "abcdefghijklmno!1",  # Longa, sem maiúscula.
    "ABCDEFGHIJKLMNO!1",  # Longa, sem minúscula.
    "Abcdefghijklmnop!",  # Longa, sem dígito.
    "Abcdefghijklmnop1",  # Longa, sem especial.
    "Abcdefghijklmn1! ",
    "Abcdefghijklmn1!aaa",
])
def test_senha_longa_invalida_nao_recebe_classificacao_de_forca(senha):
    assert ValidadorSenha().calcular_forca(senha) == "invalida"


@pytest.mark.parametrize("tamanho,forca", [(4, "fraca"), (9, "fraca"),
                                             (10, "media"), (13, "media"),
                                             (14, "forte"), (65, "forte")])
def test_forca_respeita_validacao_com_limites_personalizados(tamanho, forca):
    assert ValidadorSenha(4, 100).calcular_forca(senha_com_tamanho(tamanho)) == forca


def test_forca_respeita_minimo_e_maximo_personalizados_restritivos():
    assert ValidadorSenha(12, 20).calcular_forca(senha_com_tamanho(10)) == "invalida"
    assert ValidadorSenha(4, 12).calcular_forca(senha_com_tamanho(14)) == "invalida"


def test_chamadas_sucessivas_nao_acumulam_estado():
    validador = ValidadorSenha()
    conferir_validacao(validador, "", False, 5)
    conferir_validacao(validador, "Abcdef1!", True)
    conferir_validacao(validador, "Abcdef12", False, 1)
    conferir_validacao(validador, "Abcdef1!", True)
