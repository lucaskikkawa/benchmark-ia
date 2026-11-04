"""Testes da especificação pública de validação, pontuação e classificação."""

import itertools
import random
import string

import pytest

from senhas import ESPECIAIS, classificar, pontuar_senha, validar_senha


ESPECIAIS_ESPERADOS = frozenset("!@#$%&*?-_")
CODIGOS = (
    "curta",
    "sem_maiuscula",
    "sem_minuscula",
    "sem_digito",
    "sem_especial",
    "espaco",
)
ESPACOS = (
    " ", "\t", "\n", "\r", "\v", "\f",
    "\x1c", "\x1d", "\x1e", "\x1f", "\x85", "\xa0",
    "\u1680", "\u2000", "\u2001", "\u2002", "\u2003",
    "\u2004", "\u2005", "\u2006", "\u2007", "\u2008",
    "\u2009", "\u200a", "\u2028", "\u2029", "\u202f",
    "\u205f", "\u3000",
)


def referencia(senha, minimo=8):
    """Oráculo: conjuntos de categorias e comprimentos de blocos repetidos."""
    caracteres = set(senha)
    presentes = set()
    if set(filter(str.isupper, caracteres)):
        presentes.add("sem_maiuscula")
    if set(filter(str.islower, caracteres)):
        presentes.add("sem_minuscula")
    if caracteres.intersection(string.digits):
        presentes.add("sem_digito")
    if caracteres.intersection(ESPECIAIS_ESPERADOS):
        presentes.add("sem_especial")

    erros = set(CODIGOS[1:5]) - presentes
    if len(senha) < minimo:
        erros.add("curta")
    if set(filter(str.isspace, caracteres)):
        erros.add("espaco")
    problemas = [codigo for codigo in CODIGOS if codigo in erros]

    penalidade = 0
    for _, bloco in itertools.groupby(senha):
        comprimento = sum(1 for _ in bloco)
        penalidade += max(comprimento - 2, 0) * 10
    pontos = sorted((0, 2 * len(senha[:20]) + 15 * len(presentes) - penalidade, 100))[1]
    if "espaco" in erros:
        classe = "invalida"
    else:
        classe = ("fraca", "media", "forte")[int(pontos >= 50) + int(pontos >= 80)]
    return problemas, pontos, classe


def conferir(senha, minimo=8):
    problemas, pontos, classe = referencia(senha, minimo)
    obtidos = validar_senha(senha, tamanho_minimo=minimo)
    assert type(obtidos) is list, repr(senha)
    assert obtidos == problemas, (repr(senha), minimo)
    pontuacao = pontuar_senha(senha)
    assert type(pontuacao) is int, repr(senha)
    assert pontuacao == pontos, repr(senha)
    assert classificar(senha) == classe, repr(senha)


def test_constante_especiais():
    assert isinstance(ESPECIAIS, frozenset)
    assert ESPECIAIS == ESPECIAIS_ESPERADOS


@pytest.mark.parametrize(
    "senha,esperado",
    [
        ("", list(CODIGOS[:5])),
        (" ", list(CODIGOS)),
        ("a", ["curta", "sem_maiuscula", "sem_digito", "sem_especial"]),
        ("A", ["curta", "sem_minuscula", "sem_digito", "sem_especial"]),
        ("0", ["curta", "sem_maiuscula", "sem_minuscula", "sem_especial"]),
        ("!", ["curta", "sem_maiuscula", "sem_minuscula", "sem_digito"]),
        ("abcdefgh", ["sem_maiuscula", "sem_digito", "sem_especial"]),
        ("ABCDEFGH", ["sem_minuscula", "sem_digito", "sem_especial"]),
        ("01234567", ["sem_maiuscula", "sem_minuscula", "sem_especial"]),
        ("!@#$%&*?", ["sem_maiuscula", "sem_minuscula", "sem_digito"]),
        ("Aa0!bcde", []),
        ("Aa0!bcd", ["curta"]),
        ("Aa0! bcde", ["espaco"]),
        ("        ", list(CODIGOS[1:])),
    ],
)
def test_validacao_exemplos_e_ordem(senha, esperado):
    assert validar_senha(senha) == esperado


@pytest.mark.parametrize("minimo", [1, 2, 3, 4, 7, 8, 9, 20, 21, 64, 100])
def test_limites_do_tamanho_minimo(minimo):
    for tamanho in {0, max(0, minimo - 1), minimo, minimo + 1}:
        senha = ("Aa0!" * (tamanho // 4 + 1))[:tamanho]
        conferir(senha, minimo)
        assert ("curta" in validar_senha(senha, minimo)) == (tamanho < minimo)


@pytest.mark.parametrize("minimo", [0, -1, -8, -1000000])
@pytest.mark.parametrize("senha", ["", "Aa0!bcde"])
def test_minimo_invalido(senha, minimo):
    with pytest.raises(ValueError):
        validar_senha(senha, minimo)


@pytest.mark.parametrize("senha", [None, 0, 8, 1.5, True, b"Aa0!bcde", bytearray(b"a"), [], ["A"], {}, set(), object()])
def test_validacao_exige_string(senha):
    with pytest.raises(TypeError):
        validar_senha(senha)


def test_subclasse_de_str_e_listas_independentes():
    class Texto(str):
        pass

    conferir(Texto("Aa0!bcde"))
    conferir(Texto(" \t"))
    problemas = validar_senha("")
    problemas.clear()
    assert validar_senha("") == list(CODIGOS[:5])
    problemas = validar_senha("Aa0!bcde")
    problemas.append("intruso")
    assert validar_senha("Aa0!bcde") == []


@pytest.mark.parametrize("especial", sorted(ESPECIAIS_ESPERADOS))
def test_cada_especial_em_qualquer_posicao(especial):
    for posicao in range(8):
        senha = "Aa0bcde"
        senha = senha[:posicao] + especial + senha[posicao:]
        assert validar_senha(senha) == []
        assert pontuar_senha(senha) == 76


@pytest.mark.parametrize("digito", string.digits)
def test_cada_digito_ascii(digito):
    for posicao in range(8):
        senha = "Aa!bcde"
        senha = senha[:posicao] + digito + senha[posicao:]
        assert validar_senha(senha) == []
        assert pontuar_senha(senha) == 76


@pytest.mark.parametrize("caractere", sorted(set(string.punctuation) - ESPECIAIS_ESPERADOS))
def test_outras_pontuacoes_nao_sao_especiais(caractere):
    assert validar_senha("Aa0bcde" + caractere) == ["sem_especial"]
    assert pontuar_senha(caractere) == 2


@pytest.mark.parametrize("espaco", ESPACOS)
def test_todos_os_espacos_e_posicoes(espaco):
    for base in ("", "Aa0!bcde", "Aa0!" * 6):
        for posicao in {0, len(base) // 2, len(base)}:
            senha = base[:posicao] + espaco + base[posicao:]
            conferir(senha)
            assert "espaco" in validar_senha(senha)
            assert classificar(senha) == "invalida"
    assert validar_senha(espaco * 8) == list(CODIGOS[1:])
    assert pontuar_senha(espaco) == 2


# As categorias de caixa usam Unicode; a categoria de dígitos usa somente ASCII.
@pytest.mark.parametrize(
    "caractere,maiuscula,minuscula",
    [
        ("É", True, False), ("Ω", True, False), ("Ⅳ", True, False),
        ("é", False, True), ("ω", False, True), ("ß", False, True),
        ("ᵃ", False, True), ("\u0345", False, True),
        ("ǅ", False, False), ("中", False, False), ("😀", False, False),
        ("١", False, False), ("９", False, False), ("²", False, False),
        ("\u200b", False, False), ("\ufeff", False, False), ("\x00", False, False),
    ],
)
def test_categorias_unicode(caractere, maiuscula, minuscula):
    esperado = ["curta"]
    if not maiuscula:
        esperado.append("sem_maiuscula")
    if not minuscula:
        esperado.append("sem_minuscula")
    esperado.extend(["sem_digito", "sem_especial"])
    assert validar_senha(caractere) == esperado
    assert pontuar_senha(caractere) == 2 + 15 * (maiuscula + minuscula)
    conferir("Aa!bcde" + caractere)
    conferir("Aa0!bcde" + caractere)


@pytest.mark.parametrize("caractere", string.ascii_letters + string.digits + "!@#$%&*?-_" + " \t\n😀")
@pytest.mark.parametrize("comprimento", [1, 2, 3, 4, 5, 6, 8, 19, 20, 21, 25])
def test_blocos_repetidos_de_todas_as_categorias(caractere, comprimento):
    conferir(caractere * comprimento)
    conferir("aB0!" + caractere * comprimento + "?1Cd")


@pytest.mark.parametrize(
    "senha,pontos",
    [
        ("", 0), ("a", 17), ("aa", 19), ("aaa", 11), ("aaaa", 3),
        ("aaaaa", 0), ("ababa", 25), ("aA0!", 68),
        ("Aa0!bcde", 76), ("abcabc", 27), ("aaabbb", 7),
        ("aaabaaa", 9), ("Aa0!aaa", 64), ("Aa0!aaaa", 56),
        ("Aa0!" * 5, 100), ("Aa0!" * 6, 100),
        ("Aa0!" * 5 + "aaa", 90),
        ("Aa0!" * 5 + "aaaa", 80),
        ("Aa0!" * 5 + "aaaaa", 70),
        ("Aa0!" * 5 + "a" * 12, 0),
        ("a" * 19 + "A0!", 0),
    ],
)
def test_pontos_exatos_e_trincas_sobrepostas(senha, pontos):
    assert pontuar_senha(senha) == pontos


@pytest.mark.parametrize("tamanho", [0, 1, 2, 3, 7, 8, 9, 18, 19, 20, 21, 22, 39, 40, 41, 100, 1000])
@pytest.mark.parametrize("padrao,categorias", [("ab", 1), ("aB", 2), ("aB0", 3), ("aB0!", 4), ("./", 0)])
def test_limite_de_vinte_caracteres_e_bonus_unico(tamanho, padrao, categorias):
    senha = (padrao * (tamanho // len(padrao) + 1))[:tamanho]
    if tamanho >= len(padrao):
        assert pontuar_senha(senha) == 2 * min(tamanho, 20) + 15 * categorias
    conferir(senha)


def test_categorias_e_trincas_depois_do_vigesimo_caractere():
    base = "ab" * 10
    assert pontuar_senha(base) == 55
    assert pontuar_senha(base + "A") == 70
    assert pontuar_senha(base + "A0") == 85
    assert pontuar_senha(base + "A0!") == 100
    assert pontuar_senha(base + "aaaA0!") == 90
    # A trinca atravessa o limite dos vinte caracteres.
    assert pontuar_senha("Aa0!" * 4 + "bcaa" + "a") == 90
    # Repetições ignoram caixa apenas se o contrato o disser: aqui são distintas.
    assert pontuar_senha("aAaAaA") == 42


@pytest.mark.parametrize(
    "senha,pontos,classe",
    [
        ("", 0, "fraca"),
        ("ab" * 8, 47, "fraca"),
        ("Aa0", 51, "media"),
        ("aA0!", 68, "media"),
        ("ab" * 8 + "a", 49, "fraca"),
        ("aA" * 5, 50, "media"),
        ("ab" * 9, 51, "media"),
        ("Aa0!Aa0!A", 78, "media"),
        ("Aa0" * 5 + "Aa", 79, "media"),
        ("Aa0!Aa0!Aa", 80, "forte"),
        ("Aa0" * 6, 81, "forte"),
        ("Aa0!" * 5, 100, "forte"),
    ],
)
def test_classificacao_nos_limites_independente_de_outros_erros(senha, pontos, classe):
    assert pontuar_senha(senha) == pontos
    assert classificar(senha) == classe


def test_todas_as_combinacoes_curtas():
    # Inclui todas as ausências de categorias, ordens, repetições e espaços.
    for tamanho in range(6):
        for caracteres in itertools.product("aA0! .", repeat=tamanho):
            conferir("".join(caracteres))


def test_amostra_deterministica_de_senhas_longas_e_unicode():
    gerador = random.Random(20261104)
    alfabeto = string.ascii_letters + string.digits + string.punctuation + "ÉéΩωǅ中😀١９²\t\n\xa0\u200b\x00"
    for _ in range(1200):
        tamanho = gerador.randrange(0, 101)
        senha = "".join(gerador.choices(alfabeto, k=tamanho))
        conferir(senha, gerador.choice([1, 4, 7, 8, 9, 20, 21, 64, 101]))
