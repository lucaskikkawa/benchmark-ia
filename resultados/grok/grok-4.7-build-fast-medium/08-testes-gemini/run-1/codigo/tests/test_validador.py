"""Suíte de testes do ValidadorSenha.

Os oráculos usam a especificação (booleanos, contagem de violações e faixas
de força). O texto das mensagens não é verificado.
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from validador import CARACTERES_ESPECIAIS_PERMITIDOS, ValidadorSenha

ESPECIAIS = set("!@#$%^&*()-_+=")
BLOCO = "Ab1!Cd2@"


def senha_tamanho(n: int) -> str:
    """Senha de tamanho n com todas as classes e sem repetição tripla."""
    if n < 4:
        raise ValueError("tamanho insuficiente para cumprir as classes")
    return (BLOCO * ((n // len(BLOCO)) + 1))[:n]


def validar(senha: str, min_tam: int = 8, max_tam: int = 64):
    return ValidadorSenha(min_tam, max_tam).validar(senha)


def assert_valida(senha: str, min_tam: int = 8, max_tam: int = 64) -> None:
    ok, erros = validar(senha, min_tam, max_tam)
    assert ok is True
    assert erros == []


def assert_invalida(
    senha: str,
    min_tam: int = 8,
    max_tam: int = 64,
    n_erros: int | None = None,
) -> None:
    ok, erros = validar(senha, min_tam, max_tam)
    assert ok is False
    assert isinstance(erros, list)
    if n_erros is None:
        assert len(erros) >= 1
    else:
        assert len(erros) == n_erros


def forca(senha: str, min_tam: int = 8, max_tam: int = 64) -> str:
    return ValidadorSenha(min_tam, max_tam).calcular_forca(senha)


class TestConstante:
    def test_conjunto_exato(self):
        assert CARACTERES_ESPECIAIS_PERMITIDOS == ESPECIAIS
        assert len(CARACTERES_ESPECIAIS_PERMITIDOS) == 14
        assert " " not in CARACTERES_ESPECIAIS_PERMITIDOS
        assert "\t" not in CARACTERES_ESPECIAIS_PERMITIDOS

    def test_nao_inclui_alfanumericos(self):
        for c in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789":
            assert c not in CARACTERES_ESPECIAIS_PERMITIDOS


class TestInicializacao:
    def test_padroes(self):
        val = ValidadorSenha()
        assert val.min_tam == 8
        assert val.max_tam == 64

    def test_posicional(self):
        val = ValidadorSenha(5, 20)
        assert val.min_tam == 5
        assert val.max_tam == 20

    def test_nomeados(self):
        val = ValidadorSenha(min_tam=12, max_tam=30)
        assert val.min_tam == 12
        assert val.max_tam == 30

    def test_apenas_minimo(self):
        val = ValidadorSenha(min_tam=6)
        assert val.min_tam == 6
        assert val.max_tam == 64

    def test_apenas_maximo(self):
        val = ValidadorSenha(max_tam=16)
        assert val.min_tam == 8
        assert val.max_tam == 16

    def test_limites_iguais(self):
        val = ValidadorSenha(10, 10)
        assert val.min_tam == 10
        assert val.max_tam == 10

    def test_instancias_independentes(self):
        a = ValidadorSenha(4, 9)
        b = ValidadorSenha()
        assert a.min_tam == 4 and a.max_tam == 9
        assert b.min_tam == 8 and b.max_tam == 64


class TestComprimento:
    def test_abaixo_do_minimo_padrao(self):
        senha = senha_tamanho(7)
        assert_invalida(senha, n_erros=1)
        assert forca(senha) == "invalida"

    def test_exatamente_o_minimo_padrao(self):
        senha = senha_tamanho(8)
        assert_valida(senha)
        assert forca(senha) == "fraca"

    def test_exatamente_o_maximo_padrao(self):
        senha = senha_tamanho(64)
        assert_valida(senha)
        assert forca(senha) == "forte"

    def test_acima_do_maximo_padrao(self):
        senha = senha_tamanho(65)
        assert_invalida(senha, n_erros=1)
        assert forca(senha) == "invalida"

    def test_minimo_customizado_inclusive(self):
        assert_invalida(senha_tamanho(11), min_tam=12, max_tam=40, n_erros=1)
        assert_valida(senha_tamanho(12), min_tam=12, max_tam=40)

    def test_maximo_customizado_inclusive(self):
        assert_valida(senha_tamanho(15), min_tam=4, max_tam=15)
        assert_invalida(senha_tamanho(16), min_tam=4, max_tam=15, n_erros=1)

    def test_janela_de_um_unico_tamanho(self):
        assert_invalida(senha_tamanho(9), min_tam=10, max_tam=10, n_erros=1)
        assert_valida(senha_tamanho(10), min_tam=10, max_tam=10)
        assert_invalida(senha_tamanho(11), min_tam=10, max_tam=10, n_erros=1)

    def test_minimo_pequeno(self):
        assert_invalida(senha_tamanho(4), min_tam=5, max_tam=20, n_erros=1)
        assert_valida("Ab1!xy", min_tam=5, max_tam=20)

    def test_maximo_curto_nao_usa_o_padrao_64(self):
        assert_invalida(senha_tamanho(9), min_tam=4, max_tam=8, n_erros=1)
        assert forca(senha_tamanho(9), min_tam=4, max_tam=8) == "invalida"

    def test_minimo_alto_nao_usa_o_padrao_8(self):
        senha = senha_tamanho(8)
        assert_invalida(senha, min_tam=9, max_tam=64, n_erros=1)
        assert forca(senha, min_tam=9, max_tam=64) == "invalida"

    @pytest.mark.parametrize("n", [8, 9, 10, 13, 14, 15, 32, 63, 64])
    def test_tamanhos_intermediarios_validos(self, n):
        assert_valida(senha_tamanho(n))


class TestClassesDeCaracteres:
    def test_sem_maiuscula(self):
        assert_invalida("ab1!cdef", n_erros=1)

    def test_sem_minuscula(self):
        assert_invalida("AB1!CDEF", n_erros=1)

    def test_sem_digito(self):
        assert_invalida("Ab!Cdefg", n_erros=1)

    def test_sem_especial(self):
        assert_invalida("Ab1Cdefg", n_erros=1)

    def test_uma_de_cada_classe_no_fim(self):
        assert_valida("bcdef1A!")

    def test_uma_de_cada_classe_no_inicio(self):
        assert_valida("A!1bcdef")

    def test_digito_zero(self):
        assert_valida("Ab0!cdef")

    def test_digito_unicode_conta(self):
        # '²'.isdigit() é True; a especificação usa str.isdigit.
        assert_valida("Ab²!cdef")

    def test_numero_unicode_que_nao_e_digito_nao_conta(self):
        # '½'.isdigit() é False (embora isnumeric seja True).
        assert_invalida("Ab½!cdef", n_erros=1)

    def test_maiuscula_nao_ascii(self):
        assert_valida("Áb1!cdef")

    def test_minuscula_nao_ascii(self):
        assert_valida("Áá1!cdef")

    def test_somente_um_de_cada(self):
        assert_valida("Abcdef1!")

    @pytest.mark.parametrize("especial", sorted(ESPECIAIS))
    def test_cada_especial_permitido_basta(self, especial):
        senha = f"Ab1{especial}cdef"
        assert len(senha) == 8
        assert_valida(senha)

    @pytest.mark.parametrize(
        "proibido",
        list("~`[]{}|\\:;\"'<>,.?/¡¿·•€£§°ªº´¨"),
    )
    def test_pontuacao_fora_do_conjunto_nao_conta(self, proibido):
        senha = f"Ab1{proibido}cdef"
        assert len(senha) == 8
        assert_invalida(senha, n_erros=1)

    def test_especial_somente_no_final_da_senha_longa(self):
        assert_valida("Abcdefghijk1Z!")

    def test_letra_maiuscula_unica_no_final(self):
        assert_valida("abcdef1!Z")

    def test_letra_minuscula_unica_no_final(self):
        assert_valida("ABCDEF1!z")

    def test_digito_unico_no_final(self):
        assert_valida("Abcdefg!0")


class TestEspacos:
    @pytest.mark.parametrize(
        "branco",
        [" ", "\t", "\n", "\r", "\v", "\f", "\u00a0", "\u2003"],
    )
    def test_qualquer_espaco_invalida(self, branco):
        senha = f"Ab1!{branco}cde"
        assert len(senha) == 8
        assert_invalida(senha, n_erros=1)
        assert forca(senha) == "invalida"

    def test_espaco_no_inicio(self):
        assert_invalida(" Ab1!cde", n_erros=1)

    def test_espaco_no_fim(self):
        assert_invalida("Ab1!cde ", n_erros=1)

    def test_espaco_nao_substitui_especial(self):
        # Espaço não é especial permitido e ainda viola a regra de branco.
        assert_invalida("Ab1 cdefg", n_erros=2)

    def test_senha_valida_nao_tem_branco(self):
        assert_valida("Ab1!cdef")


class TestRepeticao:
    def test_par_repetido_e_valido(self):
        assert_valida("AAbb11!!")
        assert_valida("Ab1!cdAA")
        assert_valida("Ab1!cddE")

    def test_tres_no_inicio(self):
        assert_invalida("AAAb1!xy", n_erros=1)
        assert forca("AAAb1!xy") == "invalida"

    def test_tres_no_meio(self):
        assert_invalida("AbAAA1!x", n_erros=1)

    def test_tres_no_fim(self):
        # Única janela tripla é a última: pega off-by-one em range(len-3).
        assert_invalida("Ab1!xAAA", n_erros=1)
        assert_invalida("Ab1!c111", n_erros=1)
        assert_invalida("Ab1!c!!!", n_erros=1)

    def test_tres_especiais_no_fim_com_minimo_customizado(self):
        assert_invalida("Aa1!!!", min_tam=6, max_tam=20, n_erros=1)
        assert_valida("Aa1!!x", min_tam=6, max_tam=20)

    def test_quatro_repetidos_tambem_invalida(self):
        assert_invalida("Ab1AAAA!", n_erros=1)
        assert_invalida("AAAA1!bc", n_erros=1)

    def test_repeticao_nao_consecutiva_e_valida(self):
        assert_valida("Ab1!aAaA")
        assert_valida("A1!aA1!a")

    def test_troca_de_caixa_nao_e_repeticao(self):
        assert_valida("AaA1!bcd")
        assert_valida("aAa1!bcd")

    def test_dois_pares_separados(self):
        assert_valida("AA11bb!c")

    def test_repeticao_longa_apenas_no_limite_maximo(self):
        base = senha_tamanho(61)
        assert_valida(base + "xyZ")
        assert_invalida(base + "xxx", n_erros=1)

    def test_reuso_do_validador(self):
        val = ValidadorSenha()
        ok, erros = val.validar("Ab1!xAAA")
        assert ok is False and len(erros) == 1
        ok, erros = val.validar(senha_tamanho(8))
        assert ok is True and erros == []
        assert val.calcular_forca("Ab1!xAAA") == "invalida"
        assert val.calcular_forca(senha_tamanho(14)) == "forte"


class TestAcumuloDeErros:
    def test_varios_problemas_de_uma_vez(self):
        # curta, sem maiúscula, sem dígito, sem especial e com tripla
        ok, erros = validar("aaa")
        assert ok is False
        assert len(erros) == 5

    def test_so_espacos(self):
        ok, erros = validar("        ")
        assert ok is False
        # sem classes, com branco e com repetição; comprimento ok
        assert len(erros) == 6

    def test_curta_e_sem_classes(self):
        ok, erros = validar("")
        assert ok is False
        # curta, sem maiúscula, sem minúscula, sem dígito, sem especial
        assert len(erros) == 5

    def test_longa_demais_e_com_espaco_e_tripla(self):
        senha = "A" * 70
        ok, erros = validar(senha)
        assert ok is False
        # máximo, sem minúscula, sem dígito, sem especial, repetição
        assert len(erros) == 5

    def test_nao_para_no_primeiro_erro(self):
        # Comprimento ok; faltam maiúscula e especial.
        ok, erros = validar("abcdefg1")
        assert ok is False
        assert len(erros) == 2


class TestForca:
    def test_faixas_padrao(self):
        assert forca(senha_tamanho(8)) == "fraca"
        assert forca(senha_tamanho(9)) == "fraca"
        assert forca(senha_tamanho(10)) == "media"
        assert forca(senha_tamanho(11)) == "media"
        assert forca(senha_tamanho(12)) == "media"
        assert forca(senha_tamanho(13)) == "media"
        assert forca(senha_tamanho(14)) == "forte"
        assert forca(senha_tamanho(15)) == "forte"
        assert forca(senha_tamanho(64)) == "forte"

    def test_invalida_nas_tres_faixas(self):
        assert forca("ab1!cdef") == "invalida"
        assert forca("ab1!cdefg") == "invalida"
        assert forca(senha_tamanho(12)[:-1] + " ") == "invalida"

    def test_invalida_comprimento_10_sem_especial(self):
        senha = "Abcdefgh12"  # 10, sem especial
        assert len(senha) == 10
        assert_invalida(senha, n_erros=1)
        assert forca(senha) == "invalida"

    def test_invalida_comprimento_13_com_tripla(self):
        senha = "Ab1!cdefghAAA"
        assert len(senha) == 13
        assert_invalida(senha, n_erros=1)
        assert forca(senha) == "invalida"

    def test_invalida_comprimento_14_com_tab(self):
        senha = "Ab1!cdefghij\tK"
        assert len(senha) == 14
        assert_invalida(senha, n_erros=1)
        assert forca(senha) == "invalida"

    def test_invalida_comprimento_20(self):
        senha = "a" * 20
        assert forca(senha) == "invalida"

    def test_forca_nao_depende_do_minimo_configurado(self):
        # min 6: tamanho 6 ainda é fraca; 10 é média; 14 é forte
        assert forca(senha_tamanho(6), min_tam=6, max_tam=40) == "fraca"
        assert forca(senha_tamanho(9), min_tam=6, max_tam=40) == "fraca"
        assert forca(senha_tamanho(10), min_tam=6, max_tam=40) == "media"
        assert forca(senha_tamanho(13), min_tam=6, max_tam=40) == "media"
        assert forca(senha_tamanho(14), min_tam=6, max_tam=40) == "forte"

    def test_forca_com_minimo_alto(self):
        assert forca(senha_tamanho(12), min_tam=12, max_tam=40) == "media"
        assert forca(senha_tamanho(14), min_tam=12, max_tam=40) == "forte"
        assert forca(senha_tamanho(16), min_tam=16, max_tam=40) == "forte"
        assert forca(senha_tamanho(15), min_tam=16, max_tam=40) == "invalida"

    def test_forca_com_maximo_baixo(self):
        assert forca(senha_tamanho(9), min_tam=4, max_tam=9) == "fraca"
        assert forca(senha_tamanho(10), min_tam=4, max_tam=10) == "media"
        assert forca(senha_tamanho(10), min_tam=4, max_tam=9) == "invalida"

    def test_senha_invalida_curta_nao_e_fraca(self):
        assert forca("Ab1!") == "invalida"
        assert forca("") == "invalida"

    def test_limites_customizados_nao_alteram_rotulos(self):
        val = ValidadorSenha(min_tam=14, max_tam=14)
        assert val.calcular_forca(senha_tamanho(14)) == "forte"
        assert val.calcular_forca(senha_tamanho(13)) == "invalida"
        assert val.calcular_forca(senha_tamanho(15)) == "invalida"

    @pytest.mark.parametrize(
        ("n", "esperado"),
        [
            (8, "fraca"),
            (9, "fraca"),
            (10, "media"),
            (13, "media"),
            (14, "forte"),
            (64, "forte"),
        ],
    )
    def test_tabela_de_forca(self, n, esperado):
        senha = senha_tamanho(n)
        assert_valida(senha)
        assert forca(senha) == esperado
