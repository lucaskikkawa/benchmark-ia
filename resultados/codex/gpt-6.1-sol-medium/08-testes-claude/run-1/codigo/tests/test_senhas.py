"""Testes de contrato para validação, pontuação e classificação de senhas."""

from itertools import groupby, product
import random

import pytest

from senhas import ESPECIAIS, classificar, pontuar_senha, validar_senha


ESPECIAIS_ESPERADOS = frozenset("!@#$%&*?-_")
CODIGOS = ["curta", "sem_maiuscula", "sem_minuscula", "sem_digito", "sem_especial", "espaco"]


def categorias(senha):
    return (
        any(map(str.isupper, senha)),
        any(map(str.islower, senha)),
        bool(set(senha) & set("0123456789")),
        bool(set(senha) & ESPECIAIS_ESPERADOS),
    )


def problemas_esperados(senha, minimo=8):
    presentes = categorias(senha)
    condicoes = [len(senha) < minimo, *(not valor for valor in presentes), any(map(str.isspace, senha))]
    return [codigo for codigo, ocorre in zip(CODIGOS, condicoes) if ocorre]


def pontos_esperados(senha):
    # Uma sequência de n caracteres iguais contém max(n - 2, 0) trincas.
    penalidades = sum(max(0, len(list(grupo)) - 2) for _, grupo in groupby(senha))
    total = 2 * min(20, len(senha)) + 15 * sum(categorias(senha)) - 10 * penalidades
    return min(100, max(0, total))


def conferir(senha):
    problemas = validar_senha(senha)
    assert type(problemas) is list
    assert problemas == problemas_esperados(senha), repr(senha)
    pontos = pontuar_senha(senha)
    assert type(pontos) is int
    assert pontos == pontos_esperados(senha), repr(senha)
    esperado = "invalida" if any(map(str.isspace, senha)) else (
        "fraca" if pontos < 50 else "media" if pontos < 80 else "forte"
    )
    assert classificar(senha) == esperado, repr(senha)


def test_constante_especiais():
    assert isinstance(ESPECIAIS, frozenset)
    assert ESPECIAIS == ESPECIAIS_ESPERADOS


@pytest.mark.parametrize("senha,esperado", [
    ("", CODIGOS[:5]),
    ("        ", CODIGOS[1:]),
    ("aaaaaaaa", ["sem_maiuscula", "sem_digito", "sem_especial"]),
    ("AAAAAAAA", ["sem_minuscula", "sem_digito", "sem_especial"]),
    ("01234567", ["sem_maiuscula", "sem_minuscula", "sem_especial"]),
    ("!@#$%&*?", ["sem_maiuscula", "sem_minuscula", "sem_digito"]),
    ("Abcdef0!", []),
    ("Abcde0!", ["curta"]),
    ("Abcdefg0!", []),
    ("Ab0! ", ["curta", "espaco"]),
])
def test_validacao_exemplos(senha, esperado):
    assert validar_senha(senha) == esperado


@pytest.mark.parametrize("tamanho", [0, 1, 2, 7, 8, 9, 19, 20, 21, 40, 100])
def test_tamanho_minimo_inclusivo_e_personalizado(tamanho):
    senha = ("Aa0!" * 25)[:tamanho]
    for minimo in sorted({1, 2, 7, 8, 9, 20, 100, max(1, tamanho - 1), max(1, tamanho), tamanho + 1}):
        assert validar_senha(senha, minimo) == problemas_esperados(senha, minimo)
        assert validar_senha(senha, tamanho_minimo=minimo) == problemas_esperados(senha, minimo)


@pytest.mark.parametrize("minimo", [0, -1, -8, -1000000])
def test_minimo_invalido(minimo):
    with pytest.raises(ValueError):
        validar_senha("Aa0!abcd", minimo)


@pytest.mark.parametrize("senha", [None, 0, 8, False, 1.5, b"Aa0!abcd", bytearray(b"abc"), [], {}, (), set(), object()])
def test_tipo_invalido(senha):
    with pytest.raises(TypeError):
        validar_senha(senha)


def test_subclasse_de_str():
    class Senha(str):
        pass

    conferir(Senha("Aa0!bcde"))


@pytest.mark.parametrize("especial", sorted(ESPECIAIS_ESPERADOS))
def test_cada_especial(especial):
    assert validar_senha("Abcdefg0" + especial) == []
    assert pontuar_senha(especial) == 17
    conferir(especial * 4)


@pytest.mark.parametrize("caractere", list('"\'()+,./:;<=>[\\]^`{|}~') + ["é", "É", "中", "🙂", "\x00", "\u200b", "\ufeff"])
def test_outros_caracteres_nao_sao_especiais(caractere):
    assert validar_senha("Abcdefg0" + caractere) == ["sem_especial"]
    conferir(caractere)


@pytest.mark.parametrize("digito", "0123456789")
def test_cada_digito_ascii(digito):
    assert validar_senha("Abcdefg!" + digito) == []
    assert pontuar_senha(digito) == 17


@pytest.mark.parametrize("digito", ["²", "³", "١", "۹", "０", "𝟠", "Ⅷ", "①"])
def test_numeros_unicode_nao_sao_digitos_ascii(digito):
    assert validar_senha("Abcdefg!" + digito) == ["sem_digito"]
    conferir(digito)


@pytest.mark.parametrize("maiuscula,minuscula", [("Á", "é"), ("Ω", "λ"), ("Ж", "я"), ("Ａ", "ｚ"), ("ẞ", "ß"), ("Ǆ", "ǆ")])
def test_letras_unicode(maiuscula, minuscula):
    assert validar_senha(maiuscula + minuscula + "0!", 4) == []
    assert pontuar_senha(maiuscula + minuscula + "0!") == 68
    conferir(maiuscula)
    conferir(minuscula)


def test_letra_titlecase_nao_conta_como_maiuscula_ou_minuscula():
    assert validar_senha("ǅ0!", 1) == ["sem_maiuscula", "sem_minuscula"]
    assert pontuar_senha("ǅ") == 2


ESPACOS = list(" \t\n\r\v\f") + [chr(c) for c in (
    0x1C, 0x1D, 0x1E, 0x1F, 0x85, 0xA0, 0x1680,
    *range(0x2000, 0x200B), 0x2028, 0x2029, 0x202F, 0x205F, 0x3000,
)]


@pytest.mark.parametrize("espaco", ESPACOS)
def test_espacos_em_todas_as_posicoes(espaco):
    for senha in (espaco, espaco + "Ab0!cdef", "Ab0!" + espaco + "cdef", "Ab0!cdef" + espaco):
        assert validar_senha(senha) == problemas_esperados(senha)
        assert classificar(senha) == "invalida"
        assert pontuar_senha(senha) == pontos_esperados(senha)


@pytest.mark.parametrize("senha,pontos", [
    ("", 0), ("中", 2), ("ab", 19), ("abc", 21),
    ("aaa", 11), ("aaaa", 3), ("aaaaa", 0),
    ("aaabbb", 7), ("aaabaa", 17), ("ababab", 27),
    ("AAaa00!!", 76), ("Aa0!" * 5, 100),
    ("Aa0!" * 6, 100), ("Aa0!" * 5 + "aaa", 90),
    ("Aa0!" * 5 + "aaaa", 80), ("Aa0!" * 5 + "a" * 20, 0),
    ("中" * 3, 0), ("中🙂" * 30, 40),
])
def test_pontuacoes_exatas(senha, pontos):
    assert pontuar_senha(senha) == pontos


@pytest.mark.parametrize("senha,pontos,classe", [
    ("", 0, "fraca"), ("Ab0!", 68, "media"),
    ("ab" * 8, 47, "fraca"), ("ab" * 8 + "a", 49, "fraca"),
    ("Ab" * 5, 50, "media"), ("Ab" * 6, 54, "media"),
    ("Aa0" * 5 + "Aa", 79, "media"),
    ("Aa0!Aa0!Aa", 80, "forte"), ("Aa0!Aa0!Aa0", 82, "forte"),
    ("ab" * 20, 55, "media"), ("Aa0!" * 5, 100, "forte"),
    ("Aa0!" * 5 + " ", 100, "invalida"),
])
def test_classificacao_e_limites(senha, pontos, classe):
    assert pontuar_senha(senha) == pontos
    assert classificar(senha) == classe


def test_combinacoes_curtas():
    # Inclui todas as combinações de categorias, repetições e espaços.
    for tamanho in range(5):
        for caracteres in product("aA0!. ²", repeat=tamanho):
            conferir("".join(caracteres))


def test_variedade_de_tamanhos_categorias_e_repeticoes():
    rng = random.Random(93721)
    for _ in range(1500):
        alfabeto = rng.choice(["aA0!", "ab", "AB", "01", "!?", "中🙂", "áΩ²١_\t\u2003", "aA0!ab中🙂"])
        senha = "".join(rng.choice(alfabeto) for _ in range(rng.randrange(101)))
        conferir(senha)
        minimo = rng.choice([1, 3, 8, 20, 21, 50, 101])
        assert validar_senha(senha, minimo) == problemas_esperados(senha, minimo)


def test_trincas_em_qualquer_posicao_e_de_qualquer_categoria():
    for caractere in "aA0!中🙂\t":
        for comprimento in range(1, 26):
            bloco = caractere * comprimento
            for senha in (bloco, bloco + "Bc1?", "Bc1?" + bloco, "Bc1?" + bloco + "De2_"):
                conferir(senha)


def test_todas_as_categorias_em_tamanhos_proximos_do_teto():
    for mascara in product([False, True], repeat=4):
        prefixo = "".join(c for c, presente in zip("Aa0!", mascara) if presente)
        for tamanho in [18, 19, 20, 21, 22, 40, 100]:
            senha = prefixo + ("中🙂" * tamanho)[:tamanho - len(prefixo)]
            conferir(senha)


def test_resultados_de_validacao_independentes():
    primeiro = validar_senha("")
    primeiro.clear()
    assert validar_senha("") == CODIGOS[:5]
    assert validar_senha("Abcdef0!") == []
    assert validar_senha("") == CODIGOS[:5]
