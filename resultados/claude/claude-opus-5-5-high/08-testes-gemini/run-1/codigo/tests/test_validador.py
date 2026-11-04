import string

import pytest

from validador import CARACTERES_ESPECIAIS_PERMITIDOS, ValidadorSenha

ESPECIAIS = "!@#$%^&*()-_+="
NAO_PERMITIDOS = sorted(set(string.punctuation) - set(ESPECIAIS))


def gerar(n: int, prefixo: str = "A1!") -> str:
    """Senha válida (com padrão default) de tamanho n, sem repetições consecutivas."""
    resto = n - len(prefixo)
    assert resto >= 0
    letras = string.ascii_lowercase
    return prefixo + "".join(letras[i % 26] for i in range(resto))


def assert_valida(v, senha):
    resultado = v.validar(senha)
    assert isinstance(resultado, tuple)
    assert len(resultado) == 2
    ok, erros = resultado
    assert ok is True, (senha, erros)
    assert erros == []


def assert_invalida(v, senha, minimo_erros=1):
    ok, erros = v.validar(senha)
    assert ok is False, senha
    assert isinstance(erros, list)
    assert len(erros) >= minimo_erros, (senha, erros)
    assert all(isinstance(e, str) and e for e in erros)
    return erros


@pytest.fixture
def v():
    return ValidadorSenha()


# ---------------- Constante ----------------

def test_constante_exata():
    assert CARACTERES_ESPECIAIS_PERMITIDOS == set("!@#$%^&*()-_+=")
    assert isinstance(CARACTERES_ESPECIAIS_PERMITIDOS, set)
    assert len(CARACTERES_ESPECIAIS_PERMITIDOS) == 14


# ---------------- Construtor ----------------

def test_construtor_padrao():
    v = ValidadorSenha()
    assert v.min_tam == 8
    assert v.max_tam == 64


def test_construtor_parametros():
    v = ValidadorSenha(min_tam=5, max_tam=20)
    assert v.min_tam == 5
    assert v.max_tam == 20
    v2 = ValidadorSenha(12, 30)
    assert v2.min_tam == 12
    assert v2.max_tam == 30


# ---------------- Comprimento ----------------

def test_minimo_padrao_limite(v):
    assert_valida(v, gerar(8))
    assert_invalida(v, gerar(7))
    assert_invalida(v, gerar(4))
    assert_invalida(v, gerar(3))


def test_maximo_padrao_limite(v):
    assert_valida(v, gerar(64))
    assert_valida(v, gerar(63))
    assert_invalida(v, gerar(65))
    assert_invalida(v, gerar(100))


def test_vazia(v):
    assert_invalida(v, "", minimo_erros=5)


@pytest.mark.parametrize("min_tam,max_tam", [(4, 6), (5, 10), (12, 20), (10, 10)])
def test_limites_customizados(min_tam, max_tam):
    v = ValidadorSenha(min_tam=min_tam, max_tam=max_tam)
    assert_valida(v, gerar(min_tam))
    assert_valida(v, gerar(max_tam))
    assert_invalida(v, gerar(min_tam - 1))
    assert_invalida(v, gerar(max_tam + 1))


def test_min_customizado_maior_que_padrao():
    v = ValidadorSenha(min_tam=12)
    assert_invalida(v, gerar(8))
    assert_invalida(v, gerar(11))
    assert_valida(v, gerar(12))


def test_max_customizado_maior_que_padrao():
    v = ValidadorSenha(max_tam=100)
    assert_valida(v, gerar(65))
    assert_valida(v, gerar(100))
    assert_invalida(v, gerar(101))


def test_min_customizado_menor_que_padrao():
    v = ValidadorSenha(min_tam=4)
    assert_valida(v, "Ab1!")
    assert_valida(v, gerar(7))
    assert_invalida(v, "A1!")


def test_max_customizado_menor_que_padrao():
    v = ValidadorSenha(max_tam=10)
    assert_valida(v, gerar(10))
    assert_invalida(v, gerar(11))
    assert_invalida(v, gerar(20))


def test_comprimento_unico_erro_extra():
    # Apenas a regra de tamanho violada -> ao menos um erro; demais ok.
    v = ValidadorSenha()
    erros_curta = assert_invalida(v, "Ab1!xyz")
    erros_longa = assert_invalida(v, gerar(65))
    assert len(erros_curta) >= 1
    assert len(erros_longa) >= 1


# ---------------- Composição ----------------

def test_sem_maiuscula(v):
    assert_invalida(v, "abcdef1!")
    assert_invalida(v, "abcdefgh12!@")


def test_sem_minuscula(v):
    assert_invalida(v, "ABCDEF1!")
    assert_invalida(v, "ABCDEFGH12!@")


def test_sem_digito(v):
    assert_invalida(v, "Abcdefg!")
    assert_invalida(v, "Abcdefgh!@#$")


def test_sem_especial(v):
    assert_invalida(v, "Abcdefg1")
    assert_invalida(v, "Abcdefgh1234")


def test_uma_de_cada_basta(v):
    assert_valida(v, "aBcdef1!")
    assert_valida(v, "xyzwQ9#k")
    assert_valida(v, "1!Aabcde")
    assert_valida(v, "abcde!1Z")


@pytest.mark.parametrize("c", list(ESPECIAIS))
def test_cada_especial_permitido(v, c):
    assert_valida(v, "Abcdef1" + c)
    assert_valida(v, c + "Abcdef1")
    assert_valida(v, "Abc" + c + "def1")


@pytest.mark.parametrize("c", NAO_PERMITIDOS)
def test_pontuacao_nao_permitida(v, c):
    assert_invalida(v, "Abcdef1" + c)
    assert_invalida(v, "Abc" + c + "def12")


@pytest.mark.parametrize("c", ["é", "§", "£", "€", "°", "¿", "¡", "ç"])
def test_outros_simbolos_nao_contam(v, c):
    assert_invalida(v, "Abcdef1" + c)


def test_nao_permitido_com_permitido_eh_valido(v):
    assert_valida(v, "Abcdef1.!")
    assert_valida(v, "Ab?cd~ef1#")


def test_maiuscula_unicode(v):
    assert_valida(v, "Ébcdef1!")


def test_minuscula_unicode(v):
    assert_valida(v, "ABCDEé1!")


# ---------------- Espaços ----------------

@pytest.mark.parametrize("ws", [" ", "\t", "\n", "\r", "\x0b", "\x0c", " ", " "])
def test_espacos_proibidos(v, ws):
    assert_invalida(v, "Abcdef1!" + ws)
    assert_invalida(v, ws + "Abcdef1!")
    assert_invalida(v, "Abcd" + ws + "ef1!")


def test_espaco_unico_erro(v):
    erros = assert_invalida(v, "Abc def1!")
    assert len(erros) >= 1


# ---------------- Repetições ----------------

@pytest.mark.parametrize(
    "senha",
    [
        "aaaBcd1!",      # início
        "Abcccd1!",      # meio
        "Abcd1!xxx",     # final
        "Abcdef1!!!",    # final especial
        "Abcdef111!",    # dígitos
        "AAAbcdef1!",    # maiúsculas
        "Abcd1!zzzz",    # 4 no final
        "Abcde1!@@@",    # final, especial
        "Abcdefg1!ggg",  # final
        "Ab1!cdefgggg",
        "Abcd1!___",
    ],
)
def test_tres_repetidos_proibidos(v, senha):
    assert_invalida(v, senha)


def test_tres_repetidos_exatamente_ultimos(v):
    s = gerar(10) + "zzz"
    assert s[-3:] == "zzz"
    assert_invalida(v, s)
    # os 3 últimos caracteres formam o trio, no limite exato
    assert_invalida(v, "Ab1!cde" + "fff")


@pytest.mark.parametrize(
    "senha",
    [
        "AAbbcc11!!",
        "Aabcd11!!",
        "Abcdef1!!",
        "AAbcdef1!",
        "aaBcdef1!",
        "Abcdefg1!zz",
        "abAabAab1!",
        "Ab1!ab1!ab",
        "AaAaAa1!1!",
    ],
)
def test_dois_repetidos_permitidos(v, senha):
    assert_valida(v, senha)


def test_repeticao_nao_consecutiva_permitida(v):
    assert_valida(v, "aXaYa1!b")
    assert_valida(v, "Ab1!b1!bA")


def test_repeticao_apenas_regra_violada_com_tamanho_minimo(v):
    # 8 caracteres, repetição no final
    assert_invalida(v, "Ab1!caaa")
    # 8 caracteres, repetição no início
    assert_invalida(v, "aaaAb1!c")


def test_repeticao_senha_curta_validador_custom():
    v = ValidadorSenha(min_tam=3)
    assert_invalida(v, "aaa")
    v4 = ValidadorSenha(min_tam=4)
    assert_valida(v4, "Ab1!")
    assert_invalida(v4, "A111")


# ---------------- Acúmulo de erros ----------------

def test_acumula_todos_erros(v):
    # curta, sem maiúscula, sem dígito, sem especial, com espaço, com repetição
    erros = assert_invalida(v, "a aaa", minimo_erros=6)
    assert len(erros) >= 6


def test_acumula_dois_erros(v):
    assert_invalida(v, "abcdefg1", minimo_erros=2)  # sem maiúscula e sem especial
    assert_invalida(v, "ABCDEFGH", minimo_erros=3)  # sem minúscula, dígito, especial


def test_acumula_longa_e_composicao(v):
    assert_invalida(v, "a" + "bc" * 40, minimo_erros=4)  # longa, sem maiúscula, dígito, especial


def test_acumula_curta_e_espaco_e_repeticao():
    v = ValidadorSenha()
    erros = assert_invalida(v, "A1! aaa", minimo_erros=3)
    assert len(erros) >= 3


def test_todas_regras_mais_espaco_e_repeticao(v):
    erros = assert_invalida(v, "   ", minimo_erros=7)
    assert len(erros) >= 7


def test_contagem_erros_individual(v):
    # cada caso viola exatamente uma regra; espera-se 1 erro
    casos = [
        "Ab1!xyz",          # curta
        gerar(65),          # longa
        "abcdef1!",         # sem maiúscula
        "ABCDEF1!",         # sem minúscula
        "Abcdefg!",         # sem dígito
        "Abcdefg1",         # sem especial
        "Abc def1!",        # espaço
        "Abccc1!d",         # repetição
    ]
    for s in casos:
        ok, erros = v.validar(s)
        assert ok is False, s
        assert len(erros) == 1, (s, erros)


def test_validar_nao_altera_estado(v):
    assert_invalida(v, "abc")
    assert_valida(v, gerar(8))
    assert_invalida(v, "abc")
    assert v.min_tam == 8 and v.max_tam == 64


# ---------------- Força ----------------

@pytest.mark.parametrize("n", [8, 9])
def test_forca_fraca(v, n):
    assert v.calcular_forca(gerar(n)) == "fraca"


@pytest.mark.parametrize("n", [10, 11, 12, 13])
def test_forca_media(v, n):
    assert v.calcular_forca(gerar(n)) == "media"


@pytest.mark.parametrize("n", [14, 15, 20, 40, 63, 64])
def test_forca_forte(v, n):
    assert v.calcular_forca(gerar(n)) == "forte"


@pytest.mark.parametrize(
    "senha",
    [
        "",
        "abc",
        "Ab1!xyz",
        gerar(65),
        "abcdefghijklmn1!",       # longa, sem maiúscula
        "ABCDEFGHIJKLMN1!",       # sem minúscula
        "Abcdefghijklmn!@",       # sem dígito
        "Abcdefghijklmn12",       # sem especial
        "Abcdefg hijklm1!",       # espaço
        "Abcdefghijkl1!!!",       # repetição no final
        "Abcde1!",
        "Abcdefgh1.",             # especial não permitido, len 10
        "Abcdefgh1",              # len 9 sem especial
        "Abcdefghijk1",           # len 12 sem especial
        "Abcdef1!\t",
    ],
)
def test_forca_invalida(v, senha):
    assert v.calcular_forca(senha) == "invalida"


def test_forca_limites_customizados():
    v = ValidadorSenha(min_tam=4, max_tam=20)
    assert v.calcular_forca("Ab1!") == "fraca"
    assert v.calcular_forca(gerar(9)) == "fraca"
    assert v.calcular_forca(gerar(10)) == "media"
    assert v.calcular_forca(gerar(13)) == "media"
    assert v.calcular_forca(gerar(14)) == "forte"
    assert v.calcular_forca(gerar(20)) == "forte"
    assert v.calcular_forca(gerar(21)) == "invalida"
    assert v.calcular_forca("A1!") == "invalida"


def test_forca_respeita_max_pequeno():
    v = ValidadorSenha(max_tam=12)
    assert v.calcular_forca(gerar(12)) == "media"
    assert v.calcular_forca(gerar(13)) == "invalida"
    assert v.calcular_forca(gerar(14)) == "invalida"


def test_forca_respeita_min_grande():
    v = ValidadorSenha(min_tam=15, max_tam=64)
    assert v.calcular_forca(gerar(14)) == "invalida"
    assert v.calcular_forca(gerar(10)) == "invalida"
    assert v.calcular_forca(gerar(15)) == "forte"


def test_forca_max_grande():
    v = ValidadorSenha(max_tam=100)
    assert v.calcular_forca(gerar(80)) == "forte"


def test_forca_consistente_com_validar(v):
    for n in range(0, 70):
        s = gerar(n) if n >= 3 else "a" * n
        ok, _ = v.validar(s)
        f = v.calcular_forca(s)
        if not ok:
            assert f == "invalida"
        elif n < 10:
            assert f == "fraca"
        elif n < 14:
            assert f == "media"
        else:
            assert f == "forte"
        assert (f != "invalida") == ok
