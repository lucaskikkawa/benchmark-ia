import pytest

from senhas import ESPECIAIS, classificar, pontuar_senha, validar_senha


class TestEspeciais:
    def test_tipo_e_conteudo_exato(self):
        assert isinstance(ESPECIAIS, frozenset)
        assert ESPECIAIS == frozenset("!@#$%&*?-_")
        assert len(ESPECIAIS) == 10


class TestValidarSenha:
    def test_senha_valida_padrao(self):
        assert validar_senha("Abcdef1!") == []

    def test_limite_tamanho_minimo_padrao(self):
        assert "curta" in validar_senha("Abcde1!")  # len == 7
        assert validar_senha("Abcdef1!") == []     # len == 8

    @pytest.mark.parametrize(
        "senha,tamanho_minimo,esperado",
        [
            ("A1!a", 4, []),
            ("A1!a", 5, ["curta"]),
            ("A", 1, ["sem_minuscula", "sem_digito", "sem_especial"]),
            ("", 1, ["curta", "sem_maiuscula", "sem_minuscula", "sem_digito", "sem_especial"]),
            ("Abcdef1!Abc1", 12, []),
            ("Abcdef1!Abc", 12, ["curta"]),
        ],
    )
    def test_tamanho_minimo_customizado(self, senha, tamanho_minimo, esperado):
        assert validar_senha(senha, tamanho_minimo=tamanho_minimo) == esperado

    @pytest.mark.parametrize("tamanho_invalido", [0, -1, -10])
    def test_tamanho_minimo_invalido_levanta_value_error(self, tamanho_invalido):
        with pytest.raises(ValueError):
            validar_senha("Abcdef1!", tamanho_minimo=tamanho_invalido)

    @pytest.mark.parametrize("senha_invalida", [None, 12345678, b"Abcdef1!", ["A", "b", "1", "!"], True])
    def test_senha_nao_str_levanta_type_error(self, senha_invalida):
        with pytest.raises(TypeError):
            validar_senha(senha_invalida)

    def test_todos_os_problemas_na_ordem_correta(self):
        # " " tem len 1 (< 8), sem maiuscula, sem minuscula, sem digito, sem especial, com espaco
        assert validar_senha(" ") == [
            "curta",
            "sem_maiuscula",
            "sem_minuscula",
            "sem_digito",
            "sem_especial",
            "espaco",
        ]

    def test_string_vazia_nao_contem_espaco(self):
        assert validar_senha("") == [
            "curta",
            "sem_maiuscula",
            "sem_minuscula",
            "sem_digito",
            "sem_especial",
        ]

    def test_ordem_e_unicidade_dos_codigos(self):
        assert validar_senha("abc   def\t\n") == [
            "sem_maiuscula",
            "sem_digito",
            "sem_especial",
            "espaco",
        ]
        assert validar_senha("ABC123! ") == ["sem_minuscula", "espaco"]
        assert validar_senha("abc123! ") == ["sem_maiuscula", "espaco"]
        assert validar_senha("Abcdef! ") == ["sem_digito", "espaco"]
        assert validar_senha("Abcdef1 ") == ["sem_especial", "espaco"]

    @pytest.mark.parametrize("digito", "0123456789")
    def test_todos_digitos_ascii_aceitos(self, digito):
        assert validar_senha(f"Abcdef!{digito}") == []

    @pytest.mark.parametrize("nao_digito", ["²", "³", "٢", "Ⅳ"])
    def test_digitos_unicode_nao_ascii_nao_contam_como_digito(self, nao_digito):
        assert validar_senha(f"Abcdef!{nao_digito}") == ["sem_digito"]

    def test_unicode_isupper_e_islower(self):
        assert validar_senha("Ábcdef1!") == []
        assert validar_senha("Abcdef1!ç") == []
        assert validar_senha("ÁÉÍÓÚÇ1!") == ["sem_minuscula"]
        assert validar_senha("áéíóúç1!") == ["sem_maiuscula"]

    @pytest.mark.parametrize("especial", sorted(ESPECIAIS))
    def test_cada_caractere_de_especiais_aceito(self, especial):
        assert validar_senha(f"Abcdef1{especial}") == []

    @pytest.mark.parametrize("nao_especial", list("+=.,/\\^~()[]{}<>:;\"'`|"))
    def test_pontuacao_fora_de_especiais_rejeitada(self, nao_especial):
        assert validar_senha(f"Abcdef1{nao_especial}") == ["sem_especial"]

    @pytest.mark.parametrize("espaco", [" ", "\t", "\n", "\r", "\v", "\f", "\xa0"])
    def test_tipos_de_espaco_detectados(self, espaco):
        assert validar_senha(f"Abcdef1!{espaco}") == ["espaco"]


class TestPontuarSenha:
    def test_string_vazia(self):
        assert pontuar_senha("") == 0

    def test_pontos_por_comprimento_ate_limite_20(self):
        # 0 categorias (apenas caracteres fora de upper/lower/0-9/ESPECIAIS)
        assert pontuar_senha(".") == 2
        assert pontuar_senha(".+") == 4
        assert pontuar_senha(".+," * 6 + ".+") == 40  # len 20 -> 40
        assert pontuar_senha(".+," * 7) == 40          # len 21 -> ainda 40
        assert pontuar_senha(".+," * 10) == 40         # len 30 -> ainda 40

    def test_limite_20_com_uma_categoria(self):
        s19 = "abababababababababa"      # len 19, apenas minuscula, sem trinca
        s20 = "abababababababababab"     # len 20
        s21 = "ababababababababababa"    # len 21
        assert pontuar_senha(s19) == 19 * 2 + 15  # 53
        assert pontuar_senha(s20) == 20 * 2 + 15  # 55
        assert pontuar_senha(s21) == 20 * 2 + 15  # 55

    def test_categorias_individuais_e_combinadas(self):
        assert pontuar_senha("A") == 17      # 2 + 15
        assert pontuar_senha("a") == 17      # 2 + 15
        assert pontuar_senha("0") == 17      # 2 + 15
        assert pontuar_senha("!") == 17      # 2 + 15
        assert pontuar_senha("Á") == 17      # isupper Unicode
        assert pontuar_senha("á") == 17      # islower Unicode
        assert pontuar_senha("²") == 2       # nao conta como digito
        assert pontuar_senha("+") == 2       # nao conta como especial
        assert pontuar_senha("Aa") == 34     # 4 + 30
        assert pontuar_senha("Aa1") == 51    # 6 + 45
        assert pontuar_senha("Aa1!") == 68   # 8 + 60

    def test_categoria_repetida_conta_apenas_uma_vez(self):
        assert pontuar_senha("ABCD") == 4 * 2 + 15

    @pytest.mark.parametrize("especial", sorted(ESPECIAIS))
    def test_cada_especial_da_15_pontos(self, especial):
        assert pontuar_senha(especial) == 17

    def test_trincas_janela_deslizante(self):
        assert pontuar_senha("Ab1!xx") == 6 * 2 + 60            # 72 (0 trincas)
        assert pontuar_senha("Ab1!xxx") == 7 * 2 + 60 - 10      # 64 (1 trinca)
        assert pontuar_senha("Ab1!xxxx") == 8 * 2 + 60 - 20     # 56 (2 trincas)
        assert pontuar_senha("Ab1!xxxxx") == 9 * 2 + 60 - 30    # 48 (3 trincas)

    def test_multiplas_trincas_separadas_e_nao_consecutivas(self):
        assert pontuar_senha("Ab1!aaabbb") == 10 * 2 + 60 - 20  # 60
        assert pontuar_senha("aAa") == 3 * 2 + 30               # 36 (case-sensitive)
        assert pontuar_senha("aba") == 3 * 2 + 15               # 21 (nao consecutivos)

    def test_trinca_apos_indice_20_ainda_penaliza(self):
        base20 = "Ab1!Ab1!Ab1!Ab1!Ab1!"  # len 20, 4 categorias -> 100
        assert pontuar_senha(base20) == 100
        assert pontuar_senha(base20 + "xxx") == 90  # 40 + 60 - 10

    def test_clamp_inferior_zero_e_superior_cem(self):
        assert pontuar_senha("aaaaaaaaaa") == 0          # 20 + 15 - 80 -> 0
        assert pontuar_senha("   ") == 0                 # 6 + 0 - 10 -> 0
        assert pontuar_senha("Ab1!Ab1!Ab1!Ab1!Ab1!Ab1!") == 100  # 40 + 60 -> 100


class TestClassificar:
    @pytest.mark.parametrize(
        "senha_com_espaco",
        [
            " ",
            "Abcdef1!Abcdef1! ",
            "Abcdef1!\tAbcdef1!",
            "Abcdef1!\nAbcdef1!",
            "Abcdef1!\xa0Abcdef1!",
        ],
    )
    def test_invalida_quando_contem_espaco(self, senha_com_espaco):
        assert classificar(senha_com_espaco) == "invalida"

    def test_outros_problemas_sem_espaco_nao_geram_invalida(self):
        # Sem maiuscula e sem especial, mas sem espaco -> pontuacao 70 -> "media"
        assert classificar("abcdefghij1234567890") == "media"
        # Sem especial, mas sem espaco -> pontuacao 85 -> "forte"
        assert classificar("Abcdefghijklmnopqrst12") == "forte"

    def test_limites_fraca_media_forte(self):
        # 0 pontos -> fraca
        assert classificar("") == "fraca"
        # 49 pontos (len 17, 1 cat, sem trinca: 34 + 15 = 49) -> fraca
        s49 = "ababababababababa"
        assert pontuar_senha(s49) == 49
        assert classificar(s49) == "fraca"

        # 50 pontos (len 10, 2 cats, sem trinca: 20 + 30 = 50) -> media
        s50 = "AbAbAbAbAb"
        assert pontuar_senha(s50) == 50
        assert classificar(s50) == "media"

        # 79 pontos (len 17, 3 cats, sem trinca: 34 + 45 = 79) -> media
        s79 = "Ab1Ab1Ab1Ab1Ab1Ab"
        assert pontuar_senha(s79) == 79
        assert classificar(s79) == "media"

        # 80 pontos (len 10, 4 cats, sem trinca: 20 + 60 = 80) -> forte
        s80 = "Ab1!Ab1!Ab"
        assert pontuar_senha(s80) == 80
        assert classificar(s80) == "forte"

        # 100 pontos -> forte
        assert classificar("Ab1!Ab1!Ab1!Ab1!Ab1!") == "forte"

    def test_nao_str_levanta_type_error(self):
        with pytest.raises(TypeError):
            classificar(123)
