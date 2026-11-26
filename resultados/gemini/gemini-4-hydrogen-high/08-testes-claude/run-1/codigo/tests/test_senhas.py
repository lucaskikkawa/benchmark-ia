import pytest

from senhas import ESPECIAIS, classificar, pontuar_senha, validar_senha


# ---------------------------------------------------------------------------
# ESPECIAIS
# ---------------------------------------------------------------------------


def test_especiais_tipo_e_conteudo_exato():
    assert isinstance(ESPECIAIS, frozenset)
    esperados = frozenset("!@#$%&*?-_")
    assert ESPECIAIS == esperados
    assert len(ESPECIAIS) == 10


# ---------------------------------------------------------------------------
# validar_senha
# ---------------------------------------------------------------------------


def test_validar_senha_valida_padrao():
    assert validar_senha("Ab1!cdef") == []
    assert validar_senha("SenhaForte123!") == []


def test_validar_senha_tamanho_minimo_padrao_e_fronteiras():
    # Tamanho minimo padrao = 8
    assert validar_senha("Ab1!cde") == ["curta"]  # len 7
    assert validar_senha("Ab1!cdef") == []  # len 8
    assert validar_senha("Ab1!cdefg") == []  # len 9


@pytest.mark.parametrize("tamanho_minimo", [1, 2, 4, 8, 12, 20])
def test_validar_senha_tamanho_minimo_customizado(tamanho_minimo):
    base = "Ab1!" + "x" * 30
    exata = base[:tamanho_minimo]
    if tamanho_minimo >= 4:
        assert validar_senha(exata, tamanho_minimo=tamanho_minimo) == []
        assert validar_senha(exata, tamanho_minimo) == []
    else:
        assert "curta" not in validar_senha(exata, tamanho_minimo=tamanho_minimo)

    if tamanho_minimo > 1:
        menor = base[: tamanho_minimo - 1]
        assert "curta" in validar_senha(menor, tamanho_minimo=tamanho_minimo)
    else:
        assert "curta" in validar_senha("", tamanho_minimo=1)


@pytest.mark.parametrize("senha_invalida", [None, 123, 12.5, b"Ab1!cdef", ["A", "b", "1", "!"], True, {}])
def test_validar_senha_tipo_invalido_gera_type_error(senha_invalida):
    with pytest.raises(TypeError):
        validar_senha(senha_invalida)


@pytest.mark.parametrize("tamanho_invalido", [0, -1, -10])
def test_validar_senha_tamanho_minimo_invalido_gera_value_error(tamanho_invalido):
    with pytest.raises(ValueError):
        validar_senha("Ab1!cdef", tamanho_minimo=tamanho_invalido)


def test_validar_senha_string_vazia_todos_problemas_exceto_espaco():
    assert validar_senha("") == [
        "curta",
        "sem_maiuscula",
        "sem_minuscula",
        "sem_digito",
        "sem_especial",
    ]


def test_validar_senha_todos_os_seis_problemas_na_ordem_correta():
    assert validar_senha(" ") == [
        "curta",
        "sem_maiuscula",
        "sem_minuscula",
        "sem_digito",
        "sem_especial",
        "espaco",
    ]


def test_validar_senha_codigos_unicos_e_ordem_preservada():
    # Multiplos espacos e varios caracteres faltando -> cada codigo aparece no maximo uma vez
    assert validar_senha("   \t\n") == [
        "curta",
        "sem_maiuscula",
        "sem_minuscula",
        "sem_digito",
        "sem_especial",
        "espaco",
    ]
    assert validar_senha("ab cd ef") == [
        "sem_maiuscula",
        "sem_digito",
        "sem_especial",
        "espaco",
    ]
    assert validar_senha("AB 12 !@") == [
        "sem_minuscula",
        "espaco",
    ]
    assert validar_senha("Ab1! cd") == [
        "curta",
        "espaco",
    ]


@pytest.mark.parametrize(
    ("senha", "esperado"),
    [
        ("Ab1!cde", ["curta"]),
        ("ab1!cdef", ["sem_maiuscula"]),
        ("AB1!CDEF", ["sem_minuscula"]),
        ("Ab!cdefg", ["sem_digito"]),
        ("Ab1cdefg", ["sem_especial"]),
        ("Ab1! cdef", ["espaco"]),
        # Pares adjacentes garantem a ordem relativa exata entre todos os 6 codigos
        ("ab1!cde", ["curta", "sem_maiuscula"]),
        ("1234!@#5", ["sem_maiuscula", "sem_minuscula"]),
        ("AB!CDEFG", ["sem_minuscula", "sem_digito"]),
        ("Abcdefgh", ["sem_digito", "sem_especial"]),
        ("Ab1cdef ", ["sem_especial", "espaco"]),
    ],
)
def test_validar_senha_cada_problema_isolado_e_pares_adjacentes(senha, esperado):
    assert validar_senha(senha) == esperado


@pytest.mark.parametrize("maiuscula", ["A", "Z", "Á", "Ç", "É", "Ü"])
def test_validar_senha_maiuscula_ascii_e_unicode_em_qualquer_posicao(maiuscula):
    assert validar_senha(f"{maiuscula}bcdef1!") == []
    assert validar_senha(f"bcd{maiuscula}ef1!") == []
    assert validar_senha(f"bcdef1!{maiuscula}") == []


@pytest.mark.parametrize("minuscula", ["a", "z", "á", "ç", "é", "ü"])
def test_validar_senha_minuscula_ascii_e_unicode_em_qualquer_posicao(minuscula):
    assert validar_senha(f"{minuscula}BCDEF1!") == []
    assert validar_senha(f"BCD{minuscula}EF1!") == []
    assert validar_senha(f"BCDEF1!{minuscula}") == []


@pytest.mark.parametrize("digito", list("0123456789"))
def test_validar_senha_todos_os_digitos_ascii(digito):
    assert validar_senha(f"Abcdef!{digito}") == []


@pytest.mark.parametrize("nao_digito_ascii", ["²", "٣", "½", "①"])
def test_validar_senha_nao_aceita_digitos_unicode_fora_de_0_a_9(nao_digito_ascii):
    assert validar_senha(f"Abcdef!{nao_digito_ascii}") == ["sem_digito"]


@pytest.mark.parametrize("especial", sorted(ESPECIAIS))
def test_validar_senha_aceita_todos_caracteres_de_especiais(especial):
    assert validar_senha(f"Abcdef1{especial}") == []


@pytest.mark.parametrize(
    "nao_especial",
    [".", ",", "+", "=", "/", "\\", "^", "~", "(", ")", "[", "]", "{", "}", ":", ";", "<", ">", "|", "'", '"', "`"],
)
def test_validar_senha_rejeita_simbolos_fora_de_especiais(nao_especial):
    assert validar_senha(f"Abcdef1{nao_especial}") == ["sem_especial"]


@pytest.mark.parametrize("espaco", [" ", "\t", "\n", "\r", "\v", "\f", "\u00a0", "\u2003"])
def test_validar_senha_detecta_qualquer_isspace_em_qualquer_posicao(espaco):
    assert validar_senha(f"{espaco}Ab1!cdef") == ["espaco"]
    assert validar_senha(f"Ab1!{espaco}cdef") == ["espaco"]
    assert validar_senha(f"Ab1!cdef{espaco}") == ["espaco"]


def test_validar_senha_retorna_nova_lista_a_cada_chamada():
    r1 = validar_senha("Ab1!cdef")
    r2 = validar_senha("Ab1!cdef")
    assert r1 == r2 == []
    assert r1 is not r2


# ---------------------------------------------------------------------------
# pontuar_senha
# ---------------------------------------------------------------------------


def test_pontuar_senha_vazia_e_limites_zero_e_cem():
    assert pontuar_senha("") == 0
    assert pontuar_senha("Ab1!cdefghijklmnopqr") == 100  # 20*2 + 4*15 = 100
    assert pontuar_senha("Ab1!cdefghijklmnopqrstuvwxyz") == 100  # teto de 20 chars e teto de 100
    assert isinstance(pontuar_senha("Ab1!cdefghijklmnopqr"), int)


def test_pontuar_senha_limite_inferior_zero():
    # 10*2 + 15 - 8*10 = -45 -> limitado a 0
    assert pontuar_senha("aaaaaaaaaa") == 0
    # 5 espacos: 5*2 + 0 - 3*10 = -20 -> limitado a 0
    assert pontuar_senha("     ") == 0


def test_pontuar_senha_pontuacao_por_tamanho_e_teto_20():
    # Apenas minusculas (+15), sem trincas
    assert pontuar_senha("a") == 2 + 15
    assert pontuar_senha("ab") == 4 + 15
    assert pontuar_senha("abababababababababa") == 19 * 2 + 15  # 53 (len 19)
    assert pontuar_senha("abababababababababab") == 20 * 2 + 15  # 55 (len 20)
    assert pontuar_senha("ababababababababababa") == 20 * 2 + 15  # 55 (len 21)
    assert pontuar_senha("ababababababababababababababab") == 20 * 2 + 15  # 55 (len 30)


def test_pontuar_senha_bonus_por_categoria_unica_e_combinacoes():
    # 1 categoria (+15), independe da quantidade de ocorrencias na categoria
    assert pontuar_senha("AB") == 4 + 15
    assert pontuar_senha("ab") == 4 + 15
    assert pontuar_senha("12") == 4 + 15
    assert pontuar_senha("!@") == 4 + 15
    assert pontuar_senha("ABCD") == 8 + 15  # nao soma +15 por letra

    # Unicode upper/lower contam; digitos nao-ASCII e simbolos fora de ESPECIAIS nao contam
    assert pontuar_senha("Á") == 2 + 15
    assert pontuar_senha("á") == 2 + 15
    assert pontuar_senha("²") == 2
    assert pontuar_senha("٣") == 2
    assert pontuar_senha(".") == 2
    assert pontuar_senha(" ") == 2

    # 2, 3 e 4 categorias
    assert pontuar_senha("Ab") == 4 + 30
    assert pontuar_senha("Ab1") == 6 + 45
    assert pontuar_senha("Ab1!") == 8 + 60


@pytest.mark.parametrize("especial", sorted(ESPECIAIS))
def test_pontuar_senha_cada_especial_da_bonus(especial):
    assert pontuar_senha(especial) == 2 + 15


@pytest.mark.parametrize("digito", list("0123456789"))
def test_pontuar_senha_cada_digito_da_bonus(digito):
    assert pontuar_senha(digito) == 2 + 15


def test_pontuar_senha_trincas_janela_deslizante_e_posicoes():
    # Pares e alternancias nao penalizam
    assert pontuar_senha("aa") == 4 + 15
    assert pontuar_senha("aba") == 6 + 15
    assert pontuar_senha("AAa") == 6 + 30  # case-sensitive: 'A' != 'a'

    # 1, 2 e 3 trincas em janela deslizante
    assert pontuar_senha("aaa") == 6 + 15 - 10  # 11
    assert pontuar_senha("aaaa") == 8 + 15 - 20  # 3
    assert pontuar_senha("Ab1!aaacd") == 9 * 2 + 60 - 10  # 68 (1 trinca)
    assert pontuar_senha("Ab1!aaaacd") == 10 * 2 + 60 - 20  # 60 (2 trincas)
    assert pontuar_senha("Ab1!aaaaacd") == 11 * 2 + 60 - 30  # 52 (3 trincas)

    # Trincas no inicio, no fim e em multiplas sequencias separadas
    assert pontuar_senha("aaaAb1!cd") == 9 * 2 + 60 - 10  # 68
    assert pontuar_senha("Ab1!cdaaa") == 9 * 2 + 60 - 10  # 68
    assert pontuar_senha("aaabbb") == 6 * 2 + 15 - 20  # 7
    assert pontuar_senha("111AAA!!!") == 9 * 2 + 45 - 30  # 33

    # Trincas alem do 20o caractere continuam penalizando
    assert pontuar_senha("Ab1!cdefghijklmnopqraaa") == 40 + 60 - 10  # 90
    assert pontuar_senha("Ab1!cdefghijklmnopqaaaa") == 40 + 60 - 20  # 80


def test_pontuar_senha_categorias_apos_20o_caractere_e_espacos_no_calculo():
    # Categorias alem do 20o caractere continuam contando
    assert pontuar_senha("ababababababababababB1!") == 40 + 60  # 100
    assert pontuar_senha("ababababababababababA") == 40 + 30  # 70
    assert pontuar_senha("ABABABABABABABABABABa") == 40 + 30  # 70
    assert pontuar_senha("abababababababababab1") == 40 + 30  # 70
    assert pontuar_senha("abababababababababab!") == 40 + 30  # 70

    # Espacos contam no tamanho e em trincas (nao sao removidos por strip)
    assert pontuar_senha("Ab1! ") == 5 * 2 + 60  # 70
    assert pontuar_senha("   Ab1!") == 7 * 2 + 60 - 10  # 64


# ---------------------------------------------------------------------------
# classificar
# ---------------------------------------------------------------------------


def test_classificar_invalida_quando_tem_espaco_mesmo_com_pontuacao_alta():
    assert pontuar_senha("Ab1!cdefghijklmnopqr ") == 100
    assert classificar("Ab1!cdefghijklmnopqr ") == "invalida"
    assert classificar(" Ab1!cdefghijklmnopqr") == "invalida"
    assert classificar("Ab1!cdef\tghijklmnopqr") == "invalida"
    assert classificar("Ab1!cdef\nghijklmnopqr") == "invalida"
    assert classificar("Ab1!cdef\u00a0ghijklmnopqr") == "invalida"
    assert classificar(" ") == "invalida"


def test_classificar_outros_problemas_de_validacao_nao_tornam_invalida():
    # Sem espaco, ainda que invalida segundo validar_senha, e classificada pela pontuacao
    assert classificar("") == "fraca"
    assert classificar("abc") == "fraca"
    assert classificar("abababababababababab") == "media"  # pontos = 55, sem maiuscula/digito/especial
    assert classificar("Ab1!cde") == "media"  # curta (len 7), pontos = 74


def test_classificar_fronteiras_exatas_de_pontuacao():
    # 48 e 49 -> "fraca"
    assert pontuar_senha("AbAbAbAbA") == 48
    assert classificar("AbAbAbAbA") == "fraca"

    assert pontuar_senha("ababababababababa") == 49
    assert classificar("ababababababababa") == "fraca"

    # 50 -> "media"
    assert pontuar_senha("AbAbAbAbAb") == 50
    assert classificar("AbAbAbAbAb") == "media"

    # 78 e 79 -> "media"
    assert pontuar_senha("Ab1!cdefg") == 78
    assert classificar("Ab1!cdefg") == "media"

    assert pontuar_senha("Ab1Ab1Ab1Ab1Ab1Ab") == 79
    assert classificar("Ab1Ab1Ab1Ab1Ab1Ab") == "media"

    # 80 e 81 -> "forte"
    assert pontuar_senha("Ab1!cdefgh") == 80
    assert classificar("Ab1!cdefgh") == "forte"

    assert pontuar_senha("Ab1Ab1Ab1Ab1Ab1Ab1") == 81
    assert classificar("Ab1Ab1Ab1Ab1Ab1Ab1") == "forte"

    # 100 -> "forte"
    assert classificar("Ab1!cdefghijklmnopqr") == "forte"


@pytest.mark.parametrize("entrada_invalida", [None, 123, b"Ab1!cdef"])
def test_classificar_tipo_invalido_propaga_type_error(entrada_invalida):
    with pytest.raises(TypeError):
        classificar(entrada_invalida)
