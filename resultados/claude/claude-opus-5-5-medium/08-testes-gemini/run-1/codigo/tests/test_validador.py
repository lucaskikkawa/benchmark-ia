import pytest

from validador import CARACTERES_ESPECIAIS_PERMITIDOS, ValidadorSenha


def gerar(tam, base="Ab1!"):
    """Gera senha válida de tamanho `tam` sem 3 repetidos consecutivos."""
    assert tam >= 4
    preench = "xyzw"
    s = base + "".join(preench[i % 4] for i in range(tam - len(base)))
    assert len(s) == tam
    return s


@pytest.fixture
def v():
    return ValidadorSenha()


# ---------------- constante ----------------

def test_constante_exata():
    assert CARACTERES_ESPECIAIS_PERMITIDOS == set("!@#$%^&*()-_+=")


# ---------------- construtor ----------------

def test_defaults():
    v = ValidadorSenha()
    assert v.min_tam == 8
    assert v.max_tam == 64


def test_parametros_customizados():
    v = ValidadorSenha(min_tam=5, max_tam=20)
    assert v.min_tam == 5
    assert v.max_tam == 20
    v2 = ValidadorSenha(12, 30)
    assert v2.min_tam == 12
    assert v2.max_tam == 30


# ---------------- senha válida ----------------

def test_senha_valida_retorno_exato(v):
    assert v.validar("Abcdef1!") == (True, [])


@pytest.mark.parametrize("tam", [8, 9, 10, 20, 63, 64])
def test_tamanhos_validos_default(v, tam):
    assert v.validar(gerar(tam)) == (True, [])


# ---------------- comprimento ----------------

def test_min_exato_valido(v):
    assert v.validar("Abcde1!x") == (True, [])


def test_abaixo_min(v):
    ok, erros = v.validar("Abcd1!x")
    assert ok is False
    assert len(erros) == 1


def test_max_exato_valido(v):
    assert v.validar(gerar(64)) == (True, [])


def test_acima_max(v):
    ok, erros = v.validar(gerar(65))
    assert ok is False
    assert len(erros) == 1


def test_muito_acima_max(v):
    ok, erros = v.validar(gerar(200))
    assert ok is False
    assert len(erros) == 1


@pytest.mark.parametrize("mn,mx", [(4, 6), (5, 10), (10, 12), (12, 30)])
def test_limites_customizados(mn, mx):
    v = ValidadorSenha(min_tam=mn, max_tam=mx)
    assert v.validar(gerar(mn)) == (True, [])
    assert v.validar(gerar(mx)) == (True, [])
    ok, erros = v.validar(gerar(mn - 1)) if mn > 4 else v.validar("Ab1")
    assert ok is False and len(erros) >= 1
    ok, erros = v.validar(gerar(mx + 1))
    assert ok is False and len(erros) == 1


def test_min_customizado_abaixo_do_default():
    v = ValidadorSenha(min_tam=4)
    assert v.validar("Ab1!") == (True, [])
    assert v.validar("Ab1!xyz") == (True, [])


def test_max_customizado_acima_do_default():
    v = ValidadorSenha(max_tam=100)
    assert v.validar(gerar(65)) == (True, [])
    assert v.validar(gerar(100)) == (True, [])
    assert v.validar(gerar(101))[0] is False


def test_min_customizado_acima_do_default():
    v = ValidadorSenha(min_tam=12)
    ok, erros = v.validar(gerar(11))
    assert ok is False and len(erros) == 1
    assert v.validar(gerar(12)) == (True, [])


def test_max_customizado_abaixo_do_default():
    v = ValidadorSenha(min_tam=8, max_tam=10)
    ok, erros = v.validar(gerar(11))
    assert ok is False and len(erros) == 1


def test_min_e_max_iguais():
    v = ValidadorSenha(min_tam=8, max_tam=8)
    assert v.validar(gerar(8)) == (True, [])
    assert v.validar(gerar(7))[0] is False
    assert v.validar(gerar(9))[0] is False


# ---------------- classes de caracteres ----------------

def test_sem_maiuscula(v):
    ok, erros = v.validar("abcdef1!")
    assert ok is False and len(erros) == 1


def test_sem_minuscula(v):
    ok, erros = v.validar("ABCDEF1!")
    assert ok is False and len(erros) == 1


def test_sem_digito(v):
    ok, erros = v.validar("Abcdefg!")
    assert ok is False and len(erros) == 1


def test_sem_especial(v):
    ok, erros = v.validar("Abcdefg1")
    assert ok is False and len(erros) == 1


def test_uma_maiuscula_em_qualquer_posicao(v):
    assert v.validar("abcdef1!Z") == (True, [])
    assert v.validar("abcZdef1!") == (True, [])


def test_uma_minuscula_em_qualquer_posicao(v):
    assert v.validar("ABCDEF1!z") == (True, [])
    assert v.validar("zABCDEF1!") == (True, [])


def test_um_digito_em_qualquer_posicao(v):
    assert v.validar("Abcdefg!9") == (True, [])
    assert v.validar("0Abcdefg!") == (True, [])


@pytest.mark.parametrize("d", list("0123456789"))
def test_todos_digitos(v, d):
    assert v.validar("Abcdefg!" + d) == (True, [])


def test_maiuscula_e_minuscula_unicode(v):
    assert v.validar("Ébcdef1!") == (True, [])
    assert v.validar("ABCDEé1!") == (True, [])


@pytest.mark.parametrize("c", sorted("!@#$%^&*()-_+="))
def test_cada_especial_permitido(v, c):
    assert v.validar("Abcdef1" + c) == (True, [])
    assert v.validar(c + "Abcdef1") == (True, [])


@pytest.mark.parametrize("c", list(".,?/\\|~`'\":;<>[]{}"))
def test_pontuacao_nao_permitida_nao_conta(v, c):
    ok, erros = v.validar("Abcdef1" + c)
    assert ok is False and len(erros) == 1


def test_especial_unico_no_meio(v):
    assert v.validar("Abc#def1") == (True, [])


# ---------------- espaços ----------------

@pytest.mark.parametrize("ws", [" ", "\t", "\n", "\r", "\v", "\f", " "])
def test_espaco_em_branco(v, ws):
    ok, erros = v.validar("Abcd" + ws + "ef1!")
    assert ok is False and len(erros) == 1


def test_espaco_no_inicio_e_fim(v):
    assert v.validar(" Abcdef1!")[0] is False
    assert v.validar("Abcdef1! ")[0] is False


def test_espaco_sem_contar_como_especial(v):
    ok, erros = v.validar("Abcd ef1")
    assert ok is False and len(erros) == 2


# ---------------- repetições ----------------

@pytest.mark.parametrize("senha", [
    "aaaBcd1!",   # início
    "Abccc1!x",   # meio
    "Abcd1!xxx",  # fim
    "Ab1!1111x",  # dígitos
    "Abcd1!!!x",  # especiais
    "AAAbcd1!",   # maiúsculas
    "Abcd1!zzzz",  # 4 repetidos
])
def test_tres_repetidos(v, senha):
    ok, erros = v.validar(senha)
    assert ok is False
    assert len(erros) == 1


def test_tres_repetidos_exatamente_no_final(v):
    ok, erros = v.validar("Abcde1!!!")
    assert ok is False and len(erros) == 1
    ok, erros = v.validar("Abcdef1!@@@")
    assert ok is False and len(erros) == 1


def test_tres_repetidos_exatamente_no_inicio(v):
    ok, erros = v.validar("!!!Abcd1")
    assert ok is False and len(erros) == 1


@pytest.mark.parametrize("senha", [
    "aaBcd1!x",
    "Abcd1!xx",
    "AAbbcc11!!",
    "Abcd1!aba",
    "Ab1!Ab1!",
    "aAa1!bcd",
    "Abcd1!x1x",
])
def test_dois_repetidos_ou_nao_consecutivos_ok(v, senha):
    assert v.validar(senha) == (True, [])


def test_repetidos_case_sensitive(v):
    assert v.validar("aAaBcd1!") == (True, [])
    assert v.validar("Abc1!aAa") == (True, [])


def test_varios_blocos_repetidos_um_erro(v):
    ok, erros = v.validar("aaaBBB111!!!")
    assert ok is False
    assert len(erros) == 1


def test_espacos_repetidos(v):
    ok, erros = v.validar("Ab1!   cd")
    assert ok is False
    assert len(erros) == 2


# ---------------- acumulação de erros ----------------

def test_string_vazia(v):
    ok, erros = v.validar("")
    assert ok is False
    assert len(erros) == 5  # min, maiusc, minusc, digito, especial


def test_acumula_todos(v):
    # curta, sem maiúscula, sem dígito, sem especial, com espaço, repetida
    ok, erros = v.validar("a  aaa")
    assert ok is False
    assert len(erros) == 6


def test_acumula_longa(v):
    ok, erros = v.validar("a" * 70)
    assert ok is False
    # max, maiusc, digito, especial, repetição
    assert len(erros) == 5


def test_acumula_todas_as_oito_regras_possiveis():
    v = ValidadorSenha(min_tam=8, max_tam=2)
    # viola min? não (len>=8) -> testa separadamente
    ok, erros = v.validar("     ")
    # min, max, maiusc, minusc, digito, especial, espaço, repetição
    assert ok is False
    assert len(erros) == 8


def test_combinacoes_pares(v):
    assert len(v.validar("abcdefgh")[1]) == 3
    assert len(v.validar("ABCDEFGH")[1]) == 3
    assert len(v.validar("12345678")[1]) == 3
    assert len(v.validar("!@#$%^&*")[1]) == 3
    assert len(v.validar("Abc1!")[1]) == 1
    assert len(v.validar("abc1!")[1]) == 2


def test_erros_sao_strings_e_lista(v):
    ok, erros = v.validar("")
    assert isinstance(erros, list)
    assert all(isinstance(e, str) and e for e in erros)
    assert len(set(erros)) == len(erros)
    ok, erros = v.validar("Abcdef1!")
    assert ok is True and erros == []


def test_retorno_tupla_bool(v):
    r = v.validar("Abcdef1!")
    assert isinstance(r, tuple) and len(r) == 2
    assert r[0] is True
    r = v.validar("x")
    assert r[0] is False


def test_chamadas_independentes(v):
    v.validar("")
    assert v.validar("Abcdef1!") == (True, [])
    assert len(v.validar("")[1]) == 5


# ---------------- calcular_forca ----------------

@pytest.mark.parametrize("tam,esperado", [
    (8, "fraca"),
    (9, "fraca"),
    (10, "media"),
    (11, "media"),
    (13, "media"),
    (14, "forte"),
    (15, "forte"),
    (30, "forte"),
    (64, "forte"),
])
def test_forca_por_tamanho(v, tam, esperado):
    assert v.calcular_forca(gerar(tam)) == esperado


@pytest.mark.parametrize("senha", [
    "",
    "Abcd1!x",
    "abcdefgh1!",
    "ABCDEFGH1!",
    "Abcdefghij!",
    "Abcdefghij1",
    "Abcdefg 1!xyzw",
    "Abcdefg1!xyzwww",
    "Abcdefg1xyzw.,",
    gerar(65),
    "aaaaaaaaaaaaaaaaaaa",
])
def test_forca_invalida(v, senha):
    assert v.calcular_forca(senha) == "invalida"


def test_forca_invalida_longa_nao_e_forte(v):
    assert v.calcular_forca("abcdefghijklmnop1!") == "invalida"
    assert v.calcular_forca("Abcdefghijklmnop!!!1") == "invalida"


def test_forca_com_limites_customizados():
    v = ValidadorSenha(min_tam=4, max_tam=20)
    assert v.calcular_forca("Ab1!") == "fraca"
    assert v.calcular_forca(gerar(9)) == "fraca"
    assert v.calcular_forca(gerar(10)) == "media"
    assert v.calcular_forca(gerar(13)) == "media"
    assert v.calcular_forca(gerar(14)) == "forte"
    assert v.calcular_forca(gerar(20)) == "forte"
    assert v.calcular_forca(gerar(21)) == "invalida"


def test_forca_min_customizado_alto():
    v = ValidadorSenha(min_tam=12)
    assert v.calcular_forca(gerar(11)) == "invalida"
    assert v.calcular_forca(gerar(12)) == "media"
    assert v.calcular_forca(gerar(14)) == "forte"


def test_forca_max_customizado_baixo():
    v = ValidadorSenha(min_tam=8, max_tam=12)
    assert v.calcular_forca(gerar(12)) == "media"
    assert v.calcular_forca(gerar(13)) == "invalida"
    assert v.calcular_forca(gerar(14)) == "invalida"
    assert v.calcular_forca(gerar(9)) == "fraca"


def test_forca_repeticao_no_final(v):
    assert v.calcular_forca("Abcdefg1!xyzw") == "media"
    assert v.calcular_forca("Abcdefg1!xyzwww") == "invalida"
