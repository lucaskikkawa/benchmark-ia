import pytest
from senhas import ESPECIAIS, classificar, pontuar_senha, validar_senha

TODOS_ORDEM = [
    "curta",
    "sem_maiuscula",
    "sem_minuscula",
    "sem_digito",
    "sem_especial",
    "espaco",
]


class TestConstanteEspeciais:
    def test_tipo_frozenset(self):
        assert isinstance(ESPECIAIS, frozenset)

    def test_conteudo_exato(self):
        esperado = frozenset({"!", "@", "#", "$", "%", "&", "*", "?", "-", "_"})
        assert ESPECIAIS == esperado
        assert len(ESPECIAIS) == 10


class TestValidarSenhaExcecoes:
    @pytest.mark.parametrize(
        "entrada_invalida",
        [None, 123, 45.6, ["Ab1!abcd"], ("Ab1!abcd",), {"senha": "a"}, b"Ab1!abcd"],
    )
    def test_senha_nao_str_levanta_type_error(self, entrada_invalida):
        with pytest.raises(TypeError):
            validar_senha(entrada_invalida)

    @pytest.mark.parametrize("tamanho_invalido", [0, -1, -2, -100])
    def test_tamanho_minimo_menor_que_1_levanta_value_error(self, tamanho_invalido):
        with pytest.raises(ValueError):
            validar_senha("Ab1!abcd", tamanho_minimo=tamanho_invalido)

    def test_senha_invalida_e_tamanho_invalido_prioriza_type_error(self):
        with pytest.raises((TypeError, ValueError)):
            validar_senha(123, tamanho_minimo=0)


class TestValidarSenhaRegras:
    def test_senha_valida_padrao(self):
        resultado = validar_senha("Ab1!cdef")
        assert resultado == []
        assert isinstance(resultado, list)

    def test_tamanho_minimo_padrao_borda_7_8_9(self):
        assert validar_senha("Ab1!cde") == ["curta"]
        assert validar_senha("Ab1!cdef") == []
        assert validar_senha("Ab1!cdefg") == []

    @pytest.mark.parametrize("tam", [1, 2, 4, 10, 15])
    def test_tamanho_minimo_customizado_borda(self, tam):
        base = "Aa1!"
        senha_exata = (base * ((tam // 4) + 1))[:tam]
        if tam >= 4:
            assert validar_senha(senha_exata, tamanho_minimo=tam) == []
            assert validar_senha(senha_exata[:-1], tamanho_minimo=tam) == ["curta"]
            assert validar_senha(senha_exata, tam) == []
            assert validar_senha(senha_exata[:-1], tam) == ["curta"]

    def test_tamanho_minimo_1(self):
        assert "curta" not in validar_senha("a", tamanho_minimo=1)
        assert "curta" in validar_senha("", tamanho_minimo=1)

    def test_ordem_completa_dos_problemas(self):
        assert validar_senha("   ", tamanho_minimo=8) == TODOS_ORDEM
        assert validar_senha("", tamanho_minimo=8) == TODOS_ORDEM[:-1]

    def test_cada_problema_aparece_no_maximo_uma_vez(self):
        problemas = validar_senha("   \t\n  ", tamanho_minimo=20)
        assert problemas == TODOS_ORDEM
        assert len(problemas) == len(set(problemas))

    @pytest.mark.parametrize(
        "senha,faltando",
        [
            ("ab1!cdef", ["sem_maiuscula"]),
            ("AB1!CDEF", ["sem_minuscula"]),
            ("Abc!defg", ["sem_digito"]),
            ("Ab1cdefg", ["sem_especial"]),
            ("Ab1!cde ", ["espaco"]),
            ("Ab1!cd", ["curta"]),
        ],
    )
    def test_problema_unico_isolado(self, senha, faltando):
        assert validar_senha(senha) == faltando

    @pytest.mark.parametrize("digito", list("0123456789"))
    def test_todos_os_digitos_ascii_reconhecidos(self, digito):
        senha = f"Ab!cdef{digito}"
        assert validar_senha(senha) == []

    @pytest.mark.parametrize("falso_digito", ["\u00b2", "\u00b3", "\u0663", "\u2160"])
    def test_digitos_unicode_nao_ascii_nao_contam_como_digito(self, falso_digito):
        senha = f"Ab!cdef{falso_digito}"
        assert validar_senha(senha) == ["sem_digito"]

    @pytest.mark.parametrize("especial", list("!@#$%&*?-_"))
    def test_todos_os_especiais_reconhecidos(self, especial):
        senha = f"Ab1cdef{especial}"
        assert validar_senha(senha) == []

    @pytest.mark.parametrize(
        "nao_especial",
        list(".+,;:/\\|()[]{}<>~`'^=\"") + ["£", "€"],
    )
    def test_outros_simbolos_nao_contam_como_especial(self, nao_especial):
        senha = f"Ab1cdef{nao_especial}"
        assert validar_senha(senha) == ["sem_especial"]

    @pytest.mark.parametrize("maiuscula", ["A", "M", "Z", "Á", "Ç", "Ü"])
    def test_maiusculas_reconhecidas(self, maiuscula):
        senha = f"{maiuscula}b1!cdef"
        assert validar_senha(senha) == []

    @pytest.mark.parametrize("minuscula", ["a", "m", "z", "á", "ç", "ü"])
    def test_minusculas_reconhecidas(self, minuscula):
        senha = f"A{minuscula}1!CDEF"
        assert validar_senha(senha) == []

    @pytest.mark.parametrize("espaco", [" ", "\t", "\n", "\r", "\v", "\f", "\u00a0"])
    def test_varios_tipos_de_espaco_detectados(self, espaco):
        assert validar_senha(f"Ab1!cde{espaco}") == ["espaco"]
        assert validar_senha(f"{espaco}Ab1!cde") == ["espaco"]
        assert validar_senha(f"Ab1!{espaco}cde") == ["espaco"]


class TestPontuarSenha:
    def test_senha_vazia_pontua_zero(self):
        assert pontuar_senha("") == 0

    @pytest.mark.parametrize(
        "tamanho,esperado",
        [
            (0, 0),
            (1, 2),
            (2, 4),
            (5, 10),
            (10, 20),
            (19, 38),
            (20, 40),
            (21, 40),
            (25, 40),
            (50, 40),
        ],
    )
    def test_pontos_por_tamanho_sem_categorias_nem_trincas(self, tamanho, esperado):
        # Alterna '.' e '+' para não ter categorias nem trincas
        padrao = (".+" * ((tamanho // 2) + 1))[:tamanho]
        assert pontuar_senha(padrao) == esperado

    @pytest.mark.parametrize(
        "senha,categorias_esperadas",
        [
            (".", 0),
            ("A", 1),
            ("z", 1),
            ("0", 1),
            ("9", 1),
            ("!", 1),
            ("_", 1),
            ("Aa", 2),
            ("A1", 2),
            ("A!", 2),
            ("a1", 2),
            ("a!", 2),
            ("1!", 2),
            ("Aa1", 3),
            ("Aa!", 3),
            ("A1!", 3),
            ("a1!", 3),
            ("Aa1!", 4),
        ],
    )
    def test_pontos_por_categorias(self, senha, categorias_esperadas):
        esperado = len(senha) * 2 + categorias_esperadas * 15
        assert pontuar_senha(senha) == esperado

    @pytest.mark.parametrize("digito", list("0123456789"))
    def test_cada_digito_soma_categoria(self, digito):
        assert pontuar_senha(digito) == 17

    @pytest.mark.parametrize("falso_digito", ["\u00b2", "\u0663"])
    def test_digito_unicode_nao_soma_categoria(self, falso_digito):
        assert pontuar_senha(falso_digito) == 2

    @pytest.mark.parametrize("especial", list("!@#$%&*?-_"))
    def test_cada_especial_soma_categoria(self, especial):
        assert pontuar_senha(especial) == 17

    @pytest.mark.parametrize("nao_especial", list(".+,;:/\\|()[]{}<>~`'^=\""))
    def test_simbolo_fora_de_especiais_nao_soma_categoria(self, nao_especial):
        assert pontuar_senha(nao_especial) == 2

    def test_trincas_janela_deslizante(self):
        # Base "Aa1!" tem 4 chars (8) + 4 cats (60) = 68
        assert pontuar_senha("Aa1!bb") == 68 + 4  # 72 (0 trincas)
        assert pontuar_senha("Aa1!bbb") == 68 + 6 - 10  # 64 (1 trinca)
        assert pontuar_senha("Aa1!bbbb") == 68 + 8 - 20  # 56 (2 trincas)
        assert pontuar_senha("Aa1!bbbbb") == 68 + 10 - 30  # 48 (3 trincas)
        assert pontuar_senha("Aa1!bbbbbb") == 68 + 12 - 40  # 40 (4 trincas)

    def test_trincas_no_inicio_meio_e_fim(self):
        # 7 chars (14) + 4 cats (60) - 1 trinca (10) = 64
        assert pontuar_senha("aaaB1!c") == 64
        assert pontuar_senha("Ba111!c") == 64
        assert pontuar_senha("Ba1!ccc") == 64

    def test_multiplas_trincas_distintas(self):
        # "aaaBBB1!" -> 8 chars (16) + 4 cats (60) - 2 trincas (20) = 56
        assert pontuar_senha("aaaBBB1!") == 56

    def test_trinca_diferencia_maiuscula_e_minuscula(self):
        # "AaA" -> 3 chars (6) + 2 cats (30) - 0 trincas = 36
        assert pontuar_senha("AaA") == 36
        assert pontuar_senha("aaA") == 36
        assert pontuar_senha("Aaa") == 36

    def test_trinca_de_caracteres_alternados_nao_penaliza(self):
        # "ababab" -> 6 chars (12) + 1 cat (15) = 27
        assert pontuar_senha("ababab") == 27

    def test_limite_inferior_zero(self):
        assert pontuar_senha("...") == 0
        assert pontuar_senha("aaaaaa") == 0
        assert pontuar_senha("..........") == 0

    def test_limite_superior_100(self):
        # 20 chars (40) + 4 cats (60) = 100
        senha_20 = "Aa1!" * 5
        assert pontuar_senha(senha_20) == 100
        # 28 chars -> tamanho limitado a 20 (40) + 60 = 100
        senha_28 = "Aa1!" * 7
        assert pontuar_senha(senha_28) == 100

    def test_pontuacao_98_logo_abaixo_do_maximo(self):
        # 19 chars (38) + 4 cats (60) = 98
        senha_19 = ("Aa1!" * 5)[:19]
        assert pontuar_senha(senha_19) == 98

    def test_teto_de_tamanho_com_penalidade_de_trinca(self):
        # 23 chars -> tamanho conta como 20 (40 pts) + 4 cats (60 pts) - 1 trinca (10 pts) = 90
        # Se aplicasse min(100, ...) antes de subtrair ou não limitasse len a 20, daria outro valor!
        senha = ("Aa1!" * 5) + "bbb"
        assert len(senha) == 23
        assert pontuar_senha(senha) == 90


class TestClassificar:
    @pytest.mark.parametrize("espaco", [" ", "\t", "\n", "\r", "\v", "\f"])
    def test_senha_com_espaco_sempre_invalida(self, espaco):
        assert classificar(espaco) == "invalida"
        # Mesmo com pontuação máxima (100), ter espaço torna "invalida"
        senha_forte_com_espaco = ("Aa1!" * 5) + espaco
        assert pontuar_senha(senha_forte_com_espaco) == 100
        assert classificar(senha_forte_com_espaco) == "invalida"

    def test_borda_fraca_e_media_48_49_50_51(self):
        # 0 pontos -> fraca
        assert pontuar_senha("") == 0
        assert classificar("") == "fraca"

        # 48 pontos: 9 chars (18) + 2 cats (30) = 48 -> fraca
        s48 = "AbAbAbAbA"
        assert pontuar_senha(s48) == 48
        assert classificar(s48) == "fraca"

        # 49 pontos: 17 chars (34) + 1 cat (15) = 49 -> fraca
        s49 = "ababababababababa"
        assert pontuar_senha(s49) == 49
        assert classificar(s49) == "fraca"

        # 50 pontos: 10 chars (20) + 2 cats (30) = 50 -> media
        s50 = "AbAbAbAbAb"
        assert pontuar_senha(s50) == 50
        assert classificar(s50) == "media"

        # 51 pontos: 3 chars (6) + 3 cats (45) = 51 -> media
        s51 = "Aa1"
        assert pontuar_senha(s51) == 51
        assert classificar(s51) == "media"

    def test_borda_media_e_forte_78_79_80_81_100(self):
        # 78 pontos: 9 chars (18) + 4 cats (60) = 78 -> media
        s78 = "Aa1!Aa1!A"
        assert pontuar_senha(s78) == 78
        assert classificar(s78) == "media"

        # 79 pontos: 17 chars (34) + 3 cats (45) = 79 -> media
        s79 = ("Aa1" * 5) + "Aa"
        assert pontuar_senha(s79) == 79
        assert classificar(s79) == "media"

        # 80 pontos: 10 chars (20) + 4 cats (60) = 80 -> forte
        s80 = "Aa1!Aa1!Aa"
        assert pontuar_senha(s80) == 80
        assert classificar(s80) == "forte"

        # 81 pontos: 18 chars (36) + 3 cats (45) = 81 -> forte
        s81 = "Aa1" * 6
        assert pontuar_senha(s81) == 81
        assert classificar(s81) == "forte"

        # 100 pontos -> forte
        s100 = "Aa1!" * 5
        assert pontuar_senha(s100) == 100
        assert classificar(s100) == "forte"

    def test_classificar_senha_curta_mas_pontuacao_media_ou_forte(self):
        # "Aa1!" tem len 4 (< 8, então validar_senha tem "curta"), mas não tem "espaco"
        # Pontuação = 8 + 60 = 68 -> "media" (não "invalida"!)
        assert "curta" in validar_senha("Aa1!")
        assert pontuar_senha("Aa1!") == 68
        assert classificar("Aa1!") == "media"

        # "Aa1!Aa1" tem len 7 (< 8, tem "curta"), pontuação = 14 + 60 = 74 -> "media"
        assert classificar("Aa1!Aa1") == "media"

    def test_classificar_tipo_invalido_levanta_type_error(self):
        with pytest.raises(TypeError):
            classificar(None)
