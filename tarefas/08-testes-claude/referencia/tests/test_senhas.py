import pytest

from senhas import ESPECIAIS, classificar, pontuar_senha, validar_senha

TODOS = ["curta", "sem_maiuscula", "sem_minuscula", "sem_digito", "sem_especial"]


# ---------------- validar_senha ----------------

def test_senha_valida():
    assert validar_senha("Abcdef1!") == []


def test_tamanho_exato_nao_e_curta():
    assert "curta" not in validar_senha("Abcdef1!")  # 8 caracteres
    assert "curta" in validar_senha("Abcde1!")  # 7 caracteres


def test_tamanho_minimo_customizado():
    assert validar_senha("Ab1!", tamanho_minimo=4) == []
    assert validar_senha("Ab1!", tamanho_minimo=5) == ["curta"]
    assert validar_senha("A", tamanho_minimo=1)[0] != "curta"


def test_vazia_tem_todos_os_problemas_na_ordem():
    assert validar_senha("") == TODOS


def test_ordem_dos_problemas():
    assert validar_senha("abc") == ["curta", "sem_maiuscula", "sem_digito", "sem_especial"]
    assert validar_senha("ABCDEFGH") == ["sem_minuscula", "sem_digito", "sem_especial"]


@pytest.mark.parametrize(
    "senha, problema",
    [
        ("abcdef1!", "sem_maiuscula"),
        ("ABCDEF1!", "sem_minuscula"),
        ("Abcdefg!", "sem_digito"),
        ("Abcdefg1", "sem_especial"),
    ],
)
def test_cada_categoria_isolada(senha, problema):
    assert validar_senha(senha) == [problema]


@pytest.mark.parametrize("especial", sorted(ESPECIAIS))
def test_todos_os_especiais(especial):
    assert validar_senha("Abcdef1" + especial) == []


@pytest.mark.parametrize("branco", [" ", "\t", "\n"])
def test_espaco_em_branco(branco):
    assert validar_senha("Abcd" + branco + "ef1!") == ["espaco"]


def test_tipo_invalido():
    with pytest.raises(TypeError):
        validar_senha(12345678)
    with pytest.raises(TypeError):
        validar_senha(None)


@pytest.mark.parametrize("tamanho", [0, -1])
def test_tamanho_minimo_invalido(tamanho):
    with pytest.raises(ValueError):
        validar_senha("Abcdef1!", tamanho_minimo=tamanho)


# ---------------- pontuar_senha ----------------

def test_pontuacao_vazia():
    assert pontuar_senha("") == 0


def test_pontuacao_por_tamanho_e_categoria():
    assert pontuar_senha("ab") == 2 * 2 + 15
    assert pontuar_senha("Ab1!") == 4 * 2 + 4 * 15


def test_cada_categoria_vale_15():
    assert pontuar_senha("abcd") == 8 + 15
    assert pontuar_senha("ABCD") == 8 + 15
    assert pontuar_senha("1234") == 8 + 15
    assert pontuar_senha("!@#$") == 8 + 15


def test_tamanho_limitado_a_20():
    assert pontuar_senha("abcdefghijabcdefghij") == 40 + 15  # 20 caracteres
    assert pontuar_senha("abcdefghijabcdefghijabcde") == 40 + 15  # 25 caracteres


def test_limite_superior_100():
    assert pontuar_senha("Abcdefghij1!abcdefgh") == 100


def test_trincas_janela_deslizante():
    assert pontuar_senha("xaaab") == 10 + 15 - 10
    assert pontuar_senha("xaaaab") == 12 + 15 - 20
    assert pontuar_senha("xyaaaaab") == 16 + 15 - 30  # "aaaaa" = 3 trincas
    assert pontuar_senha("Abc1!zzzzzz") == 22 + 60 - 40


def test_limite_inferior_zero():
    assert pontuar_senha("aaaaaaaa") == 0


# ---------------- classificar ----------------

def test_classificar_faixas_e_limites():
    assert pontuar_senha("abcdefgh12") == 50
    assert classificar("abcdefgh12") == "media"
    assert pontuar_senha("abcdefgh1") == 48
    assert classificar("abcdefgh1") == "fraca"
    assert pontuar_senha("Abcdefgh12") == 65
    assert classificar("Abcdefgh12") == "media"
    assert pontuar_senha("Abcdefgh1!") == 80
    assert classificar("Abcdefgh1!") == "forte"
    assert pontuar_senha("Abcdefg1!") == 78
    assert classificar("Abcdefg1!") == "media"


def test_classificar_invalida_com_espaco():
    assert classificar("Abcdefghij 1!xyz") == "invalida"
    assert classificar("Abcdefghij\t1!xyz") == "invalida"


def test_classificar_curta_nao_e_invalida():
    assert classificar("a") == "fraca"


# ---------------- bordas de definição (Unicode, tipos, constante) ----------------

@pytest.mark.parametrize("digito", ["٣", "１", "²", "১"])
def test_digito_nao_ascii_nao_conta(digito):
    # "de 0 a 9": dígitos de outros alfabetos não contam (embora str.isdigit() seja True).
    assert validar_senha("Abcdefg!" + digito) == ["sem_digito"]
    assert pontuar_senha("ab" + digito) == 3 * 2 + 15


def test_sublinhado_e_especial():
    assert validar_senha("Abcdefg1_") == []
    assert pontuar_senha("x_") == 4 + 15 + 15


def test_especiais_exatos():
    assert ESPECIAIS == frozenset("!@#$%&*?-_")
    for nao_especial in ".,;:/+=^~()[]{}<>'\"\\|`":
        assert "sem_especial" in validar_senha("Abcdef1" + nao_especial)


@pytest.mark.parametrize("branco", ["\r", "\x0b", "\x0c", " ", " ", "　"])
def test_qualquer_isspace_e_espaco(branco):
    assert validar_senha("Abcd" + branco + "ef1!") == ["espaco"]
    assert classificar("Abcdefghij" + branco + "1!xyz") == "invalida"


def test_espaco_e_ultimo_da_lista():
    assert validar_senha(" ") == ["curta", "sem_maiuscula", "sem_minuscula", "sem_digito", "sem_especial", "espaco"]


@pytest.mark.parametrize("valor", [b"Abcdef1!", ["A", "b", "1", "!"], ("A", "b"), bytearray(b"Ab1!")])
def test_tipos_iteraveis_nao_str(valor):
    with pytest.raises(TypeError):
        validar_senha(valor)


def test_trinca_no_final():
    assert pontuar_senha("Abc1!zzz") == 16 + 60 - 10
    assert pontuar_senha("aaa") == max(0, 6 + 15 - 10)
    assert pontuar_senha("Ab1!xyzwvuuu") == 24 + 60 - 10


def test_letras_sem_caixa_nao_contam():
    # "中" é letra (isalpha), mas não é maiúscula nem minúscula.
    assert validar_senha("中中中中1!ab") == ["sem_maiuscula"]
    assert validar_senha("中中中中1!AB") == ["sem_minuscula"]
