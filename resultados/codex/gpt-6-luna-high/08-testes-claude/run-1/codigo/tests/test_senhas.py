import pytest

from senhas import ESPECIAIS, classificar, pontuar_senha, validar_senha


def test_especiais_contem_exatamente_os_caracteres_documentados():
    assert ESPECIAIS == frozenset("!@#$%&*?-_")
    assert isinstance(ESPECIAIS, frozenset)


@pytest.mark.parametrize(
    ("senha", "esperado"),
    [
        ("Abcdef1!", []),
        ("Abcdef1", ["curta", "sem_especial"]),
        ("", ["curta", "sem_maiuscula", "sem_minuscula", "sem_digito", "sem_especial"]),
        ("abcdefgh", ["sem_maiuscula", "sem_digito", "sem_especial"]),
        ("ABCDEFGH", ["sem_minuscula", "sem_digito", "sem_especial"]),
        ("12345678", ["sem_maiuscula", "sem_minuscula", "sem_especial"]),
        ("!!!!!!!!", ["sem_maiuscula", "sem_minuscula", "sem_digito"]),
        ("Abcdef1! ", ["espaco"]),
        ("Abcdef1!\t", ["espaco"]),
        ("Abcdef1!\n", ["espaco"]),
        ("Abcdef1!\u00a0", ["espaco"]),
    ],
)
def test_validar_senha_retorna_problemas_na_ordem_especificada(senha, esperado):
    resultado = validar_senha(senha)
    assert resultado == esperado
    assert len(resultado) == len(set(resultado))


@pytest.mark.parametrize(
    ("senha", "esperado"),
    [
        # isupper/islower são Unicode, mas dígitos e especiais são ASCII/exatos.
        ("Äbcdefg1!", []),
        ("äBCDEFG1!", []),
        ("Abcdefg١!", ["sem_digito"]),
        ("Abcdefg1.", ["sem_especial"]),
    ],
)
def test_validar_senha_usa_as_categorias_documentadas(senha, esperado):
    assert validar_senha(senha) == esperado


@pytest.mark.parametrize(
    ("senha", "minimo", "esperado"),
    [
        ("Abcdef1!", 8, []),
        ("Abcdef1!", 9, ["curta"]),
        ("Abcdef1!", 1, []),
        ("Abcdef1!", 20, ["curta"]),
        ("Abcdef1!", 8, []),
        ("", 1, ["curta", "sem_maiuscula", "sem_minuscula", "sem_digito", "sem_especial"]),
    ],
)
def test_tamanho_minimo_configuravel(senha, minimo, esperado):
    assert validar_senha(senha, tamanho_minimo=minimo) == esperado


@pytest.mark.parametrize("senha", [None, 1, 1.5, b"Abcdef1!", ["Abcdef1!"]])
def test_validar_senha_rejeita_senha_que_nao_e_str(senha):
    with pytest.raises(TypeError):
        validar_senha(senha)


@pytest.mark.parametrize("minimo", [0, -1, -100])
def test_validar_senha_rejeita_tamanho_minimo_menor_que_um(minimo):
    with pytest.raises(ValueError):
        validar_senha("Abcdef1!", minimo)


def test_validar_senha_verifica_tipo_da_senha_antes_do_tamanho():
    with pytest.raises(TypeError):
        validar_senha(None, 0)


@pytest.mark.parametrize(
    ("senha", "esperado"),
    [
        ("", 0),
        ("a", 17),  # 2 pontos pelo caractere e 15 pela categoria minúscula.
        ("A", 17),
        ("1", 17),
        ("!", 17),
        ("ab", 19),
        ("Ab1!", 68),
        ("Ab1.", 53),  # pontuação especial só para ESPECIAIS.
        ("Ab١!", 53),  # algarismo Unicode não conta como dígito ASCII.
        ("Ää1!", 68),  # maiúscula/minúscula usam os métodos Unicode.
    ],
)
def test_pontuacao_por_comprimento_e_categorias(senha, esperado):
    assert pontuar_senha(senha) == esperado


@pytest.mark.parametrize("n, desconto", [(2, 0), (3, 10), (4, 20), (5, 30), (6, 40)])
def test_trincas_iguais_sao_contadas_em_janelas_deslizantes(n, desconto):
    # A base inclui 15 pela categoria minúscula.
    assert pontuar_senha("a" * n) == max(0, 2 * n + 15 - desconto)


@pytest.mark.parametrize(
    ("senha", "esperado"),
    [
        ("aaab", 13),  # uma trinca consecutiva
        ("aabaa", 25),  # duas ocorrências não sobrepostas? nenhuma trinca
        ("abcccde", 19),  # uma trinca dentro de uma senha com categoria minúscula
        ("aaaAAA", 22),  # trincas são sensíveis a maiúsculas/minúsculas
    ],
)
def test_trincas_sao_consecutivas_e_exatas(senha, esperado):
    assert pontuar_senha(senha) == esperado


def test_pontuacao_limita_comprimento_a_vinte_caracteres():
    assert pontuar_senha("a" * 20) == 0  # limite antes da penalidade de trincas
    assert pontuar_senha("a" * 21) == 0
    assert pontuar_senha("abcdefghijklmnopqrst") == 55
    assert pontuar_senha("abcdefghijklmnopqrstu") == 55


def test_pontuacao_tem_teto_de_cem_e_piso_de_zero():
    # Sem trincas, comprimento 20 e quatro categorias dariam 100.
    assert pontuar_senha("Abcdefghijklmno1!pqr") == 100
    assert pontuar_senha("a" * 100) == 0


@pytest.mark.parametrize(
    ("senha", "esperado"),
    [
        ("abcdefghijklmnopq", 49),
        ("Abcdefghij", 50),
        ("Abcdefghijklmn1pq", 79),
        ("Abcdef1!xy", 80),
    ],
)
def test_classificar_respeita_limites_exatos_de_pontuacao(senha, esperado):
    assert pontuar_senha(senha) == esperado
    faixa = "fraca" if esperado < 50 else "media" if esperado < 80 else "forte"
    assert classificar(senha) == faixa


@pytest.mark.parametrize("senha", ["Abcdef1! ", "Abcdef1!\t", "Abcdef1!\n"])
def test_classificar_prioriza_espaco_independentemente_da_pontuacao(senha):
    assert classificar(senha) == "invalida"


@pytest.mark.parametrize(
    ("senha", "esperado"),
    [
        ("", "fraca"),
        ("Abcdef1!", "media"),
    ],
)
def test_classificar_nao_trata_outros_problemas_de_validacao_como_invalida(senha, esperado):
    assert classificar(senha) == esperado

