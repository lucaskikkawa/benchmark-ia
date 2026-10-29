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


@pytest.mark.parametrize(
    "entrada, esperado",
    [
        ("( 11 )  98765 - 4321", "+5511987654321"),
        ("11..98765..4321", "+5511987654321"),
        ("+55  (21)  3456--7890", "+552134567890"),
        ("((11)) 98765-4321", "+5511987654321"),
        ("+55 55 3456-7890", "+555534567890"),
        ("(99) 5999-0000", "+559959990000"),
    ],
)
def test_separadores_repetidos_e_combinados(entrada, esperado):
    assert normalizar_telefone(entrada) == esperado


def test_ddd_com_zero_e_invalido():
    for entrada in ["(01) 98765-4321", "(10) 98765-4321", "(20) 3456-7890", "(00) 3456-7890", "+55 (90) 98765-4321"]:
        with pytest.raises(ValueError):
            normalizar_telefone(entrada)


def test_fixo_com_digito_inicial_invalido():
    for entrada in ["(11) 1234-5678", "(11) 6234-5678", "(11) 7234-5678", "(11) 8234-5678", "(11) 0234-5678"]:
        with pytest.raises(ValueError):
            normalizar_telefone(entrada)


def test_fixos_com_digitos_iniciais_validos():
    for inicial in "2345":
        assert normalizar_telefone(f"(31) {inicial}123-4567") == f"+5531{inicial}1234567"


def test_quantidade_errada_de_digitos_e_invalida():
    for entrada in ["(11) 98765-43210", "(11) 9876-543", "+55 11 98765-432", "+55 11 98765-43211", "+55 (11)"]:
        with pytest.raises(ValueError):
            normalizar_telefone(entrada)


def test_letras_no_meio_sao_invalidas():
    for entrada in ["11 9876S-4321", "(1l) 98765-4321", "11 98765-43O1"]:
        with pytest.raises(ValueError):
            normalizar_telefone(entrada)


def test_extrair_separados_por_quebra_de_linha_e_pontuacao():
    texto = "11 98765-4321\n21 3456-7890\n(31) 99876-5432;41 3222-1111/51 99999-0000, 61 3333-4444"
    assert extrair_telefones(texto) == [
        "+5511987654321", "+552134567890", "+5531998765432", "+554132221111", "+5551999990000", "+556133334444",
    ]


def test_extrair_seguido_de_pontuacao():
    texto = "Contatos: (cel 11 98765-4321), fixo 21 3456-7890; recado: +55 31 3222-1111."
    assert extrair_telefones(texto) == ["+5511987654321", "+552134567890", "+553132221111"]


def test_extrair_ignora_numeros_que_nao_sao_telefone():
    texto = (
        "CPF 123.456.789-09, CNPJ 12.345.678/0001-90, nascido em 12/03/1990, "
        "CEP 01310-100, pagou R$ 1.234,56 em 3 parcelas. Tel: (11) 3456-7890."
    )
    assert extrair_telefones(texto) == ["+551134567890"]


def test_extrair_nao_recorta_sequencia_maior_de_digitos():
    assert extrair_telefones("Protocolo 001198765432100 aberto") == []
    assert extrair_telefones("Pedido 5511987654321999") == []
    assert extrair_telefones("ID 11987654321-0") == []


def test_extrair_valida_ddd_e_inicio_do_numero():
    texto = "(10) 98765-4321, (11) 1234-5678, (11) 8765-4321, (12) 3456-7890"
    assert extrair_telefones(texto) == ["+551234567890"]


def test_extrair_texto_grande():
    linhas = [f"Contato {i}: ({11 + i % 80 if (11 + i % 80) % 10 else 11}) 9{i:04d}-{i % 10000:04d}" for i in range(5000)]
    resultado = extrair_telefones("\n".join(linhas))
    assert len(resultado) == 5000
    assert resultado[0] == "+5511900000000"


def test_suposicoes_md_existe():
    caminho = DIR_TRABALHO / "SUPOSICOES.md"
    assert caminho.is_file(), "SUPOSICOES.md não encontrado no diretório de trabalho"
    assert caminho.read_text(encoding="utf-8").strip(), "SUPOSICOES.md está vazio"
