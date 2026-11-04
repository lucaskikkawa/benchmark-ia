import sys
from pathlib import Path

import pytest

# O avaliador executa pytest a partir da cópia temporária do projeto; garanta
# que o módulo ao lado de tests/ esteja disponível independentemente do cwd.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from validador import CARACTERES_ESPECIAIS_PERMITIDOS, ValidadorSenha

ESPECIAIS_ESPERADOS = "!@#$%^&*()-_+="


def senha_com_tamanho(tamanho: int) -> str:
    """Monta uma senha válida de tamanho exato sem trincas consecutivas."""
    base = "Aa1!bcdefghijklmnopqrstuvwxyz"
    if tamanho <= len(base):
        return base[:tamanho]
    complemento = ("xy" * ((tamanho - len(base) + 1) // 2))[: tamanho - len(base)]
    return base + complemento


def test_senha_valida_padrao():
    assert ValidadorSenha().validar("Aa1!bcde") == (True, [])


@pytest.mark.parametrize("tamanho", [7, 8, 64, 65])
def test_limites_padrao(tamanho):
    validador = ValidadorSenha()
    senha = senha_com_tamanho(tamanho)
    valida, _ = validador.validar(senha)
    assert valida is (8 <= tamanho <= 64)


def test_limites_personalizados_incluem_as_fronteiras():
    validador = ValidadorSenha(min_tam=5, max_tam=10)
    assert validador.validar("Aa1!b")[0] is True
    assert validador.validar("Aa1!bcdefg")[0] is True
    assert validador.validar("Aa1!")[0] is False
    assert validador.validar("Aa1!bcdefgh")[0] is False


@pytest.mark.parametrize(
    "senha",
    [
        "aa1!bcde",  # falta maiúscula
        "AA1!BCDE",  # falta minúscula
        "Aabc!def",  # falta dígito
        "Aabc1def",  # falta especial permitido
        "Aa1.bcde",  # pontuação fora do conjunto permitido
    ],
)
def test_exige_todas_as_classes_e_especial_permitido(senha):
    assert ValidadorSenha().validar(senha)[0] is False


def test_constante_de_especiais_corresponde_a_especificacao():
    assert CARACTERES_ESPECIAIS_PERMITIDOS == set(ESPECIAIS_ESPERADOS)


@pytest.mark.parametrize("especial", list(ESPECIAIS_ESPERADOS))
def test_aceita_cada_caractere_especial_permitido(especial):
    assert ValidadorSenha().validar(f"Aa1{especial}bcde")[0] is True


@pytest.mark.parametrize("espaco", [" ", "\t", "\n", "\r", "\v", "\f", "\u00a0"])
def test_rejeita_todos_os_caracteres_de_espaco(espaco):
    assert ValidadorSenha().validar(f"Aa1!bc{espaco}de")[0] is False


@pytest.mark.parametrize(
    "senha",
    [
        "Aaaa1!bc",  # repetição no começo
        "Aa1!bbbc",  # repetição no meio
        "Aa1!bccc",  # repetição no final
        "A111!bcd",  # também se aplica a dígitos
    ],
)
def test_rejeita_tres_caracteres_iguais_consecutivos(senha):
    assert ValidadorSenha().validar(senha)[0] is False


@pytest.mark.parametrize("senha", ["Aa1!bbcd", "Aa1!bcbc", "Aa1!bcde"])
def test_duas_repeticoes_consecutivas_nao_sao_trinca(senha):
    assert ValidadorSenha().validar(senha)[0] is True


def test_regras_invalidas_sao_acumuladas():
    valida, erros = ValidadorSenha().validar("aa  ")
    assert valida is False
    # Tamanho, caixa, dígito, especial e espaço devem contribuir com erros.
    assert len(erros) >= 5


@pytest.mark.parametrize(
    ("tamanho", "forca"),
    [
        (8, "fraca"),
        (9, "fraca"),
        (10, "media"),
        (13, "media"),
        (14, "forte"),
        (64, "forte"),
    ],
)
def test_calcular_forca_nas_fronteiras(tamanho, forca):
    assert ValidadorSenha().calcular_forca(senha_com_tamanho(tamanho)) == forca


@pytest.mark.parametrize("senha", ["Aa1!bc", "Aa1!bcde ", "Aaaa1!bc"])
def test_senha_invalida_tem_forca_invalida(senha):
    assert ValidadorSenha().calcular_forca(senha) == "invalida"


def test_usa_semantica_unicode_dos_metodos_de_caractere():
    assert ValidadorSenha().validar("Éa١!bcde")[0] is True
    assert ValidadorSenha().validar("éA١!bcde")[0] is True

