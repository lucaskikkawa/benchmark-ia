import sys
from pathlib import Path

import pytest

# Garante que `validador.py` seja importável tanto a partir da raiz do projeto
# quanto de uma cópia de `tests/` isolada em outro diretório.
_RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_RAIZ))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from validador import CARACTERES_ESPECIAIS_PERMITIDOS, ValidadorSenha  # noqa: E402


SENHA_PADRAO = "Abcdef1!"  # 8 caracteres, cumpre todas as regras


def senha_com_tamanho(n: int) -> str:
    """Gera senha de tamanho `n` (>= 4) que cumpre todas as regras e não tem triplas."""
    return ("Aa1!" + "bcd" * n)[:n]


def contar_erros(senha: str, validador: ValidadorSenha | None = None) -> int:
    validador = validador or ValidadorSenha()
    _, erros = validador.validar(senha)
    return len(erros)


# ---------------------------------------------------------------------------
# Constante
# ---------------------------------------------------------------------------

def test_constante_caracteres_especiais():
    assert CARACTERES_ESPECIAIS_PERMITIDOS == set("!@#$%^&*()-_+=")


# ---------------------------------------------------------------------------
# validar: caso válido e retorno
# ---------------------------------------------------------------------------

def test_senha_valida_retorna_true_e_lista_vazia():
    assert ValidadorSenha().validar(SENHA_PADRAO) == (True, [])


def test_retorno_invalido_eh_tupla_bool_e_lista():
    valida, erros = ValidadorSenha().validar("abc")
    assert valida is False
    assert isinstance(erros, list)
    assert all(isinstance(e, str) for e in erros)


# ---------------------------------------------------------------------------
# Regra 1 e 2: comprimento mínimo e máximo (limites inclusivos)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("tamanho", [8, 9, 10, 20, 63, 64])
def test_comprimentos_dentro_dos_limites_padrao_sao_validos(tamanho):
    assert ValidadorSenha().validar(senha_com_tamanho(tamanho)) == (True, [])


def test_abaixo_do_minimo_padrao_eh_invalido():
    senha = senha_com_tamanho(7)
    assert ValidadorSenha().validar(senha)[0] is False
    assert contar_erros(senha) == 1


def test_acima_do_maximo_padrao_eh_invalido():
    senha = senha_com_tamanho(65)
    assert ValidadorSenha().validar(senha)[0] is False
    assert contar_erros(senha) == 1


def test_minimo_customizado_aceita_igual_ao_limite():
    v = ValidadorSenha(min_tam=4, max_tam=6)
    assert v.validar(senha_com_tamanho(4)) == (True, [])


def test_minimo_customizado_rejeita_um_abaixo():
    v = ValidadorSenha(min_tam=5, max_tam=6)
    assert contar_erros(senha_com_tamanho(4), v) == 1
    assert v.validar(senha_com_tamanho(5)) == (True, [])


def test_maximo_customizado_aceita_igual_ao_limite():
    v = ValidadorSenha(min_tam=4, max_tam=6)
    assert v.validar(senha_com_tamanho(6)) == (True, [])


def test_maximo_customizado_rejeita_um_acima():
    v = ValidadorSenha(min_tam=4, max_tam=6)
    assert contar_erros(senha_com_tamanho(7), v) == 1


def test_limites_customizados_nao_usam_padrao():
    # Com min_tam=4, senha de 5 caracteres deve ser válida (o padrão 8 não se aplica).
    v = ValidadorSenha(min_tam=4, max_tam=6)
    assert v.validar(senha_com_tamanho(5)) == (True, [])


# ---------------------------------------------------------------------------
# Regras 3, 4, 5: maiúscula, minúscula, dígito (uma por vez)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "senha",
    [
        "abcdefg1!",   # sem maiúscula
        "abcdefgh1!",  # sem maiúscula (tamanho maior)
    ],
)
def test_sem_maiuscula_eh_invalido(senha):
    assert ValidadorSenha().validar(senha)[0] is False
    assert contar_erros(senha) == 1


@pytest.mark.parametrize(
    "senha",
    [
        "ABCDEFG1!",   # sem minúscula
        "ABCDEFGH1!",  # sem minúscula (tamanho maior)
    ],
)
def test_sem_minuscula_eh_invalido(senha):
    assert ValidadorSenha().validar(senha)[0] is False
    assert contar_erros(senha) == 1


@pytest.mark.parametrize(
    "senha",
    [
        "Abcdefg!",    # sem dígito
        "Abcdefgh!",   # sem dígito (tamanho maior)
    ],
)
def test_sem_digito_eh_invalido(senha):
    assert ValidadorSenha().validar(senha)[0] is False
    assert contar_erros(senha) == 1


# ---------------------------------------------------------------------------
# Regra 6: caractere especial pertencente a CARACTERES_ESPECIAIS_PERMITIDOS
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("especial", sorted(CARACTERES_ESPECIAIS_PERMITIDOS))
def test_cada_caractere_especial_permitido_eh_aceito(especial):
    senha = "Abcdef1" + especial
    assert ValidadorSenha().validar(senha) == (True, [])


@pytest.mark.parametrize(
    "pontuacao",
    ["~", ".", ",", "/", "?", ";", ":", "'", '"', "`", "<", ">", "|", "\\", "[", "]", "{", "}"],
)
def test_pontuacao_fora_do_conjunto_nao_conta_como_especial(pontuacao):
    senha = "Abcdef1" + pontuacao
    assert ValidadorSenha().validar(senha)[0] is False
    assert contar_erros(senha) == 1


def test_sem_especial_eh_invalido():
    assert contar_erros("Abcdefg1") == 1


# ---------------------------------------------------------------------------
# Regra 7: espaços em branco
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("espaco", [" ", "\t", "\n", "\r", "\x0b", "\x0c"])
def test_espaco_em_branco_no_meio_eh_invalido(espaco):
    senha = "Abcde" + espaco + "f1!"
    assert ValidadorSenha().validar(senha)[0] is False
    assert contar_erros(senha) == 1


@pytest.mark.parametrize("espaco", [" ", "\t", "\n"])
def test_espaco_em_branco_no_inicio_ou_fim_eh_invalido(espaco):
    assert contar_erros(espaco + "Abcdef1!") == 1
    assert contar_erros("Abcdef1!" + espaco) == 1


# ---------------------------------------------------------------------------
# Regra 8: três caracteres repetidos consecutivos
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "senha",
    [
        "aaaBcde1!",   # tripla no início
        "Abbbcde1!",   # tripla no meio
        "Abc111de!",   # tripla de dígitos no meio
        "Abcde1!!!",   # tripla no final
        "Abcdddd1!",   # quádrupla contém tripla
    ],
)
def test_tres_caracteres_repetidos_consecutivos_sao_invalidos(senha):
    assert ValidadorSenha().validar(senha)[0] is False
    assert contar_erros(senha) == 1


def test_tripla_ocupando_as_tres_ultimas_posicoes_eh_detectada():
    # Cobre o limite do laço: a última janela de 3 caracteres também deve ser verificada.
    assert contar_erros("Abcdef1yyy!") == 1
    assert contar_erros("Abcdef1!!!") == 1


def test_duas_repeticoes_consecutivas_sao_validas():
    assert ValidadorSenha().validar("Aabbcc1!") == (True, [])
    assert ValidadorSenha().validar("Abccdef1!") == (True, [])


def test_repeticao_nao_consecutiva_eh_valida():
    assert ValidadorSenha().validar("Abababa1!") == (True, [])


def test_maiuscula_e_minuscula_nao_formam_tripla():
    # "Aaa" tem apenas 2 minúsculas idênticas; "A" != "a" para a regra de triplas.
    assert ValidadorSenha().validar("Aaabcde1!") == (True, [])


# ---------------------------------------------------------------------------
# Acúmulo de erros
# ---------------------------------------------------------------------------

def test_erros_sao_acumulados_e_nao_interrompidos_no_primeiro():
    # "abc": min (8), maiúscula, dígito, especial -> 4 violações
    valida, erros = ValidadorSenha().validar("abc")
    assert valida is False
    assert len(erros) == 4


def test_triplas_somam_ao_acumulo_de_outros_erros():
    # "aaa": min, maiúscula, dígito, especial, tripla -> 5 violações
    assert contar_erros("aaa") == 5


def test_senha_vazia_gera_erros_de_regras_de_conteudo():
    # "": min, maiúscula, minúscula, dígito, especial -> 5 violações
    valida, erros = ValidadorSenha().validar("")
    assert valida is False
    assert len(erros) == 5


def test_acima_do_maximo_com_regras_faltando_acumula_erros():
    # 70 'a': max, maiúscula, dígito, especial, tripla -> 5 violações
    assert contar_erros("a" * 70) == 5


# ---------------------------------------------------------------------------
# calcular_forca
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "senha",
    [
        "abc",                        # inválida (curta e sem regras)
        "Abcdef1",                    # inválida: sem especial e curta
        "abcdefghij",                 # comprimento 10, mas sem maiúscula/dígito/especial
        "Abcdefghijklmnopqrs1",       # comprimento 21, sem especial
        "Abbbcdefgh1!ij",             # comprimento 14 com tripla
    ],
)
def test_forca_senha_invalida_retorna_invalida(senha):
    assert ValidadorSenha().calcular_forca(senha) == "invalida"


def test_forca_senha_longa_mas_com_espaco_eh_invalida():
    # Comprimento exatamente 14, válido em tamanho, mas inválido por espaço.
    base = senha_com_tamanho(14)
    senha = base[:5] + " " + base[6:]
    assert len(senha) == 14
    assert ValidadorSenha().calcular_forca(senha) == "invalida"


@pytest.mark.parametrize("tamanho", [8, 9])
def test_forca_fraca_para_tamanhos_abaixo_de_10(tamanho):
    assert ValidadorSenha().calcular_forca(senha_com_tamanho(tamanho)) == "fraca"


@pytest.mark.parametrize("tamanho", [10, 11, 12, 13])
def test_forca_media_para_tamanhos_entre_10_e_13(tamanho):
    assert ValidadorSenha().calcular_forca(senha_com_tamanho(tamanho)) == "media"


@pytest.mark.parametrize("tamanho", [14, 15, 20, 64])
def test_forca_forte_para_tamanhos_a_partir_de_14(tamanho):
    assert ValidadorSenha().calcular_forca(senha_com_tamanho(tamanho)) == "forte"


def test_limites_de_forca_exatos():
    v = ValidadorSenha()
    assert v.calcular_forca(senha_com_tamanho(9)) == "fraca"
    assert v.calcular_forca(senha_com_tamanho(10)) == "media"
    assert v.calcular_forca(senha_com_tamanho(13)) == "media"
    assert v.calcular_forca(senha_com_tamanho(14)) == "forte"


def test_forca_usa_limites_customizados():
    v = ValidadorSenha(min_tam=4, max_tam=6)
    assert v.calcular_forca(senha_com_tamanho(4)) == "fraca"
    assert v.calcular_forca(senha_com_tamanho(6)) == "fraca"
    assert v.calcular_forca(senha_com_tamanho(7)) == "invalida"
