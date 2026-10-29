from pathlib import Path

import pytest

from telefones import extrair_telefones, normalizar_telefone

DIR_TRABALHO = Path(__file__).resolve().parent.parent


# Somente o núcleo explícito do enunciado é testado.

@pytest.mark.parametrize(
    "entrada, esperado",
    [
        ("+55 (11) 98765-4321", "+5511987654321"),
        ("(21) 3456-7890", "+552134567890"),
        ("11987654321", "+5511987654321"),
    ],
)
def test_exemplos_do_enunciado(entrada, esperado):
    assert normalizar_telefone(entrada) == esperado


@pytest.mark.parametrize(
    "entrada",
    ["+5511987654321", "5511987654321", "55 11 98765 4321", "+55.11.98765.4321", "(11)98765-4321", "11 98765-4321"],
)
def test_variacoes_de_celular(entrada):
    assert normalizar_telefone(entrada) == "+5511987654321"


@pytest.mark.parametrize("entrada", ["2134567890", "+55 21 3456-7890", "552134567890", "21.3456.7890"])
def test_variacoes_de_fixo(entrada):
    assert normalizar_telefone(entrada) == "+552134567890"


def test_espacos_nas_bordas():
    assert normalizar_telefone("  (31) 99876-5432  ") == "+5531998765432"


@pytest.mark.parametrize(
    "entrada",
    [
        "telefone",
        "",
        "123",
        "abc-defg",
        "98765-4321-1234-5678-99",
        "987654321",  # 9 dígitos, sem DDD
        "11876543210",  # DDD + 9 dígitos que não começam com 9
    ],
)
def test_invalidos(entrada):
    with pytest.raises(ValueError):
        normalizar_telefone(entrada)


def test_extrair_exemplo_do_enunciado():
    texto = "Ligar para (11) 98765-4321 ou 21 3456-7890 à tarde"
    assert extrair_telefones(texto) == ["+5511987654321", "+552134567890"]


def test_extrair_sem_repeticao_e_ordem():
    texto = "Cel: 21 99999-8888. Fixo: (11) 3456-7890. Repetindo o cel: +55 21 99999-8888."
    assert extrair_telefones(texto) == ["+5521999998888", "+551134567890"]


def test_extrair_texto_sem_telefones():
    assert extrair_telefones("Cliente prefere contato por e-mail.") == []
    assert extrair_telefones("") == []


def test_suposicoes_md_existe():
    caminho = DIR_TRABALHO / "SUPOSICOES.md"
    assert caminho.is_file(), "SUPOSICOES.md não encontrado no diretório de trabalho"
    assert caminho.read_text(encoding="utf-8").strip(), "SUPOSICOES.md está vazio"
