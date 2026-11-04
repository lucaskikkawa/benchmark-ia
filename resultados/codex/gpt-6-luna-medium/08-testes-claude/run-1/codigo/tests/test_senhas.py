import pytest

from senhas import ESPECIAIS, classificar, pontuar_senha, validar_senha


def test_especiais_e_uma_frozenset_com_o_conjunto_especificado():
    assert isinstance(ESPECIAIS, frozenset)
    assert ESPECIAIS == frozenset("!@#$%&*?-_")


@pytest.mark.parametrize(
    ("senha", "minimo", "esperado"),
    [
        ("", 8, ["curta", "sem_maiuscula", "sem_minuscula", "sem_digito", "sem_especial"]),
        ("abcdefg", 8, ["curta", "sem_maiuscula", "sem_digito", "sem_especial"]),
        ("ABCDEFG", 8, ["curta", "sem_minuscula", "sem_digito", "sem_especial"]),
        ("1234567", 8, ["curta", "sem_maiuscula", "sem_minuscula", "sem_especial"]),
        ("!!!!!!!", 8, ["curta", "sem_maiuscula", "sem_minuscula", "sem_digito"]),
        ("Abc123!", 8, ["curta"]),
        ("Abc123!x", 8, []),
        ("Abc123!x", 9, ["curta"]),
        ("Abc123!x", 1, []),
        ("Abc123!\nx", 8, ["espaco"]),
    ],
)
def test_validar_senha_regras_ordem_e_minimo(senha, minimo, esperado):
    assert validar_senha(senha, minimo) == esperado


@pytest.mark.parametrize("espaco", [" ", "\t", "\n", "\r", "\v", "\f", "\u00a0", "\u2003"])
def test_todo_caractere_isspace_e_detectado(espaco):
    assert validar_senha("Aa1!" + espaco + "bcde") == ["espaco"]


@pytest.mark.parametrize("especial", sorted(ESPECIAIS))
def test_cada_especial_e_aceito(especial):
    assert "sem_especial" not in validar_senha("Abc1234" + especial)
    assert pontuar_senha(especial) == 17


@pytest.mark.parametrize("caractere", ["é", "Ω", "中", "١", "²", ".", "+", "/", "~"])
def test_unicode_e_simbolos_nao_sao_digitos_ascii_ou_especiais(caractere):
    problemas = validar_senha("Abcdefg" + caractere)
    assert "sem_digito" in problemas
    assert "sem_especial" in problemas
    categorias = sum((caractere.isupper(), caractere.islower()))
    assert pontuar_senha(caractere) == 2 + 15 * categorias


@pytest.mark.parametrize("senha", [None, 1, 1.5, b"Abc123!x", ["A"], object()])
def test_validar_rejeita_senha_que_nao_e_string(senha):
    with pytest.raises(TypeError):
        validar_senha(senha)


@pytest.mark.parametrize("minimo", [0, -1, -100])
def test_validar_rejeita_minimo_menor_que_um(minimo):
    with pytest.raises(ValueError):
        validar_senha("Abc123!x", minimo)


def test_tipo_e_validado_antes_do_minimo():
    with pytest.raises(TypeError):
        validar_senha(None, 0)


@pytest.mark.parametrize("senha", ["", "a", "aa", "ab"])
def test_pontuacao_curta(senha):
    assert pontuar_senha(senha) == 2 * len(senha) + (15 if any(c.islower() for c in senha) else 0)


@pytest.mark.parametrize(
    ("senha", "esperado"),
    [
        ("A", 17),                 # caractere + maiúscula
        ("a", 17),                 # caractere + minúscula
        ("0", 17),                 # caractere + dígito ASCII
        ("!", 17),                 # caractere + especial
        ("Aa", 34),
        ("Aa0", 51),
        ("Aa0!", 68),
        ("Aa0!x", 70),
        ("Aa0!xxxx", 76),
        ("Aa0!xxxxxxxx", 84),
    ],
)
def test_pontuacao_por_comprimento_e_categorias(senha, esperado):
    assert pontuar_senha(senha) == esperado


def test_comprimento_contribui_ate_vinte_caracteres():
    assert pontuar_senha("a" * 20) == 55  # 40 + 15
    assert pontuar_senha("a" * 21) == 57  # caractere extra não pontua
    assert pontuar_senha("a" * 40) == 0   # 40 + 15 - 38*10, limitado a zero


@pytest.mark.parametrize(
    ("senha", "trincas"),
    [("aaa", 1), ("aaaa", 2), ("aaaaa", 3), ("aaab", 1), ("aabaa", 0), ("aaXaaa", 1)],
)
def test_penalidade_por_janelas_sobrepostas_de_tres_iguais(senha, trincas):
    base = min(len(senha), 20) * 2 + (15 if any(c.islower() for c in senha) else 0)
    assert pontuar_senha(senha) == max(0, min(100, base - 10 * trincas))


def test_trincas_sao_exatas_inclusive_digitos_e_especiais():
    assert pontuar_senha("111") == 0
    assert pontuar_senha("!!!") == 0
    assert pontuar_senha("aaA") == 36


@pytest.mark.parametrize(
    ("senha", "esperado"),
    [
        ("", "fraca"),
        ("Abc123!\n", "invalida"),
        ("A" * 17, "fraca"),  # 34 + 15 = 49
        ("A" * 18, "media"),  # 36 + 15 = 51
        ("A" * 20, "media"),  # 40 + 15 = 55
        ("Aa0!" + "x" * 4, "media"),  # 16 + 60 = 76
        ("Aa0!" + "x" * 6, "forte"),  # 20 + 60 = 80
    ],
)
def test_classificar_limites_e_espacos(senha, esperado):
    assert classificar(senha) == esperado


def test_classificar_espaco_tem_precedencia_sobre_pontuacao():
    senha = "Aa0!" + "x" * 30 + " "
    assert pontuar_senha(senha) == 100
    assert classificar(senha) == "invalida"

