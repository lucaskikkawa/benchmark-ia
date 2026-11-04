import inspect
import pytest
import senhas
from senhas import ESPECIAIS, classificar, pontuar_senha, validar_senha


class TestEspeciais:
    def test_tipo_frozenset(self):
        assert isinstance(ESPECIAIS, frozenset)
        assert type(ESPECIAIS) is frozenset

    def test_conteudo_exato(self):
        esperado = frozenset({"!", "@", "#", "$", "%", "&", "*", "?", "-", "_"})
        assert ESPECIAIS == esperado
        assert len(ESPECIAIS) == 10

    @pytest.mark.parametrize("char", list("!@#$%&*?-_"))
    def test_cada_caractere_presente(self, char):
        assert char in ESPECIAIS

    @pytest.mark.parametrize(
        "char",
        list(".,;:+=/\\|~`'\"<>()[]{}^ \t\n0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"),
    )
    def test_outros_caracteres_ausentes(self, char):
        assert char not in ESPECIAIS


class TestValidarSenhaExcecoesAssinatura:
    def test_assinatura_valor_padrao(self):
        sig = inspect.signature(validar_senha)
        assert sig.parameters["tamanho_minimo"].default == 8

    @pytest.mark.parametrize(
        "entrada_invalida",
        [
            None,
            123,
            0,
            12.34,
            b"Abcdef1!",
            bytearray(b"Abcdef1!"),
            ["A", "b", "c", "d", "e", "f", "1", "!"],
            ("Abcdef1!",),
            {"senha": "Abcdef1!"},
            frozenset("Abcdef1!"),
            True,
            False,
        ],
    )
    def test_senha_nao_str_levanta_type_error(self, entrada_invalida):
        with pytest.raises(TypeError):
            validar_senha(entrada_invalida)

    def test_senha_nao_str_com_tamanho_invalido_prioriza_type_error(self):
        with pytest.raises(TypeError):
            validar_senha(123, tamanho_minimo=0)

    def test_subclasse_de_str_aceita(self):
        class MinhaStr(str):
            pass

        assert validar_senha(MinhaStr("Abcdef1!")) == []

    @pytest.mark.parametrize("tamanho", [0, -1, -2, -10, -100])
    def test_tamanho_minimo_menor_que_1_levanta_value_error(self, tamanho):
        with pytest.raises(ValueError):
            validar_senha("Abcdef1!", tamanho_minimo=tamanho)
        with pytest.raises(ValueError):
            validar_senha("", tamanho_minimo=tamanho)

    def test_tamanho_minimo_1_valido(self):
        assert validar_senha("Ab1!", tamanho_minimo=1) == []
        assert "curta" in validar_senha("", tamanho_minimo=1)
        assert "curta" not in validar_senha("a", tamanho_minimo=1)


class TestValidarSenhaRegras:
    def test_senha_valida_retorna_lista_vazia(self):
        res = validar_senha("Abcdef1!")
        assert res == []
        assert type(res) is list

    def test_tamanho_padrao_fronteira_7_8_9(self):
        assert validar_senha("Abcde1!") == ["curta"]
        assert validar_senha("Abcdef1!") == []
        assert validar_senha("Abcdefg1!") == []

    @pytest.mark.parametrize(
        "tamanho_minimo,senha_curta,senha_ok",
        [
            (1, "", "A"),
            (4, "Ab!", "Ab1!"),
            (5, "Ab1!", "Abc1!"),
            (8, "Abcde1!", "Abcdef1!"),
            (10, "Abcdefg1!", "Abcdefgh1!"),
            (15, "Abcdefghijkl1!", "Abcdefghijklm1!"),
        ],
    )
    def test_tamanho_minimo_customizado_fronteira(self, tamanho_minimo, senha_curta, senha_ok):
        assert "curta" in validar_senha(senha_curta, tamanho_minimo=tamanho_minimo)
        assert "curta" not in validar_senha(senha_ok, tamanho_minimo=tamanho_minimo)

    def test_cada_problema_isoladamente(self):
        assert validar_senha("Abcde1!") == ["curta"]
        assert validar_senha("abcdef1!") == ["sem_maiuscula"]
        assert validar_senha("ABCDEF1!") == ["sem_minuscula"]
        assert validar_senha("Abcdefg!") == ["sem_digito"]
        assert validar_senha("Abcdefg1") == ["sem_especial"]
        assert validar_senha("Abcdef1! ") == ["espaco"]

    def test_ordem_exata_todos_os_problemas(self):
        # String vazia: 5 problemas na ordem especificada
        assert validar_senha("") == [
            "curta",
            "sem_maiuscula",
            "sem_minuscula",
            "sem_digito",
            "sem_especial",
        ]
        # Apenas espaços curtos: todos os 6 problemas na ordem especificada
        assert validar_senha("   ") == [
            "curta",
            "sem_maiuscula",
            "sem_minuscula",
            "sem_digito",
            "sem_especial",
            "espaco",
        ]
        # 8 espaços: 5 problemas (sem "curta") na ordem especificada
        assert validar_senha("        ") == [
            "sem_maiuscula",
            "sem_minuscula",
            "sem_digito",
            "sem_especial",
            "espaco",
        ]

    def test_codigos_aparecem_no_maximo_uma_vez(self):
        problemas = validar_senha("   ")
        assert len(problemas) == len(set(problemas))
        assert validar_senha("Abcdef1!   ") == ["espaco"]

    @pytest.mark.parametrize("maiuscula", ["A", "M", "Z", "Á", "Ç", "Ü", "Ω"])
    def test_maiuscula_reconhecida_em_qualquer_posicao(self, maiuscula):
        assert validar_senha(f"{maiuscula}bcdef1!") == []
        assert validar_senha(f"abc{maiuscula}ef1!") == []
        assert validar_senha(f"abcdef1!{maiuscula}") == []

    @pytest.mark.parametrize("minuscula", ["a", "m", "z", "á", "ç", "ü", "ß"])
    def test_minuscula_reconhecida_em_qualquer_posicao(self, minuscula):
        assert validar_senha(f"{minuscula}BCDEF1!") == []
        assert validar_senha(f"ABC{minuscula}EF1!") == []
        assert validar_senha(f"ABCDEF1!{minuscula}") == []

    @pytest.mark.parametrize("digito", list("0123456789"))
    def test_cada_digito_0_a_9_reconhecido_em_qualquer_posicao(self, digito):
        assert validar_senha(f"{digito}Abcdef!") == []
        assert validar_senha(f"Abc{digito}def!") == []
        assert validar_senha(f"Abcdef!{digito}") == []

    @pytest.mark.parametrize("nao_digito_ascii", ["²", "³", "¹", "\u0660", "\u0669", "Ⅳ", "/'", ":"])
    def test_digitos_unicode_ou_adjacentes_ascii_nao_contam_como_digito(self, nao_digito_ascii):
        assert "sem_digito" in validar_senha(f"Abcdef!{nao_digito_ascii}")

    @pytest.mark.parametrize("especial", list("!@#$%&*?-_"))
    def test_cada_especial_reconhecido_em_qualquer_posicao(self, especial):
        assert validar_senha(f"{especial}Abcdef1") == []
        assert validar_senha(f"Abc{especial}def1") == []
        assert validar_senha(f"Abcdef1{especial}") == []

    @pytest.mark.parametrize("nao_especial", list(".,;:+=/\\|~`'\"<>()[]{}^"))
    def test_outros_simbolos_nao_contam_como_especial(self, nao_especial):
        assert validar_senha(f"Abcdef1{nao_especial}") == ["sem_especial"]

    @pytest.mark.parametrize("espaco", [" ", "\t", "\n", "\r", "\v", "\f", "\u00a0", "\u2003"])
    def test_qualquer_isspace_gera_espaco_em_qualquer_posicao(self, espaco):
        assert validar_senha(f"{espaco}Abcdef1!") == ["espaco"]
        assert validar_senha(f"Abc{espaco}def1!") == ["espaco"]
        assert validar_senha(f"Abcdef1!{espaco}") == ["espaco"]


class TestPontuarSenha:
    @pytest.mark.parametrize("n", list(range(0, 26)) + [30, 50])
    def test_pontos_apenas_por_tamanho_sem_categorias_nem_trincas(self, n):
        # "." e "+" não pertencem a nenhuma categoria e alternados não formam trincas
        senha = (".+" * ((n // 2) + 1))[:n]
        esperado = min(n, 20) * 2
        res = pontuar_senha(senha)
        assert res == esperado
        assert type(res) is int

    def test_tamanho_limite_19_20_21_com_todas_categorias(self):
        # 19 chars, 4 categorias, 0 trincas -> 38 + 60 = 98
        s19 = "Abcdefghijklmnop1!q"
        assert len(s19) == 19
        assert pontuar_senha(s19) == 98

        # 20 chars, 4 categorias, 0 trincas -> 40 + 60 = 100
        s20 = "Abcdefghijklmnop1!qr"
        assert len(s20) == 20
        assert pontuar_senha(s20) == 100

        # 21 chars, 4 categorias, 0 trincas -> 40 + 60 = 100
        s21 = "Abcdefghijklmnop1!qrs"
        assert len(s21) == 21
        assert pontuar_senha(s21) == 100

    @pytest.mark.parametrize(
        "senha,categorias_esperadas",
        [
            ("", 0),
            (".", 0),
            (".+", 0),
            ("A", 1),
            ("Z", 1),
            ("Á", 1),
            ("a", 1),
            ("z", 1),
            ("ç", 1),
            ("0", 1),
            ("5", 1),
            ("9", 1),
            ("!", 1),
            ("_", 1),
            ("-", 1),
            ("AB", 1),
            ("ab", 1),
            ("12", 1),
            ("!@", 1),
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
            ("Aa1!Bb2@", 4),
        ],
    )
    def test_pontuacao_por_categorias(self, senha, categorias_esperadas):
        esperado = len(senha) * 2 + 15 * categorias_esperadas
        assert pontuar_senha(senha) == esperado

    @pytest.mark.parametrize("digito", list("0123456789"))
    def test_cada_digito_soma_15_pontos(self, digito):
        assert pontuar_senha(digito) == 17

    @pytest.mark.parametrize("falso_digito", ["²", "³", "\u0660", "/", ":"])
    def test_falso_digito_nao_soma_categoria(self, falso_digito):
        assert pontuar_senha(falso_digito) == 2

    @pytest.mark.parametrize("especial", list("!@#$%&*?-_"))
    def test_cada_especial_soma_15_pontos(self, especial):
        assert pontuar_senha(especial) == 17

    @pytest.mark.parametrize("falso_especial", list(".,;:+=/\\|~`'\"<>()[]{}^ "))
    def test_falso_especial_nao_soma_categoria(self, falso_especial):
        assert pontuar_senha(falso_especial) == 2

    def test_pares_e_repeticoes_alternadas_nao_descontam_trinca(self):
        # Pares consecutivos não são trincas
        assert pontuar_senha("AA") == 4 + 15
        assert pontuar_senha("AAbb11!!") == 16 + 60
        # Caracteres iguais alternados ("AbA", "AbAbA") não são trincas
        assert pontuar_senha("AbA") == 6 + 30
        assert pontuar_senha("AbAbA") == 10 + 30
        # Diferença de maiúscula/minúscula ("AAa", "aAA", "aAa") não forma trinca
        assert pontuar_senha("AAa") == 6 + 30
        assert pontuar_senha("aAA") == 6 + 30
        assert pontuar_senha("aAa") == 6 + 30

    def test_trincas_em_janela_deslizante(self):
        # "aaa": len 3 (6) + 1 cat (15) - 1 trinca (10) = 11
        assert pontuar_senha("aaa") == 11
        # "aaaa": len 4 (8) + 1 cat (15) - 2 trincas (20) = 3
        assert pontuar_senha("aaaa") == 3
        # "aaaaB1!": len 7 (14) + 4 cats (60) - 2 trincas (20) = 54
        assert pontuar_senha("aaaaB1!") == 54
        # "aaaaaB1!": len 8 (16) + 4 cats (60) - 3 trincas (30) = 46
        assert pontuar_senha("aaaaaB1!") == 46
        # "aaaaaaB1!": len 9 (18) + 4 cats (60) - 4 trincas (40) = 38
        assert pontuar_senha("aaaaaaB1!") == 38

    def test_trinca_no_inicio_meio_e_fim(self):
        # Trinca no início
        assert pontuar_senha("aaaB1!") == 12 + 60 - 10
        # Trinca no meio
        assert pontuar_senha("Baaa1!") == 12 + 60 - 10
        # Trinca no fim
        assert pontuar_senha("B1!aaa") == 12 + 60 - 10
        # Múltiplas trincas separadas
        assert pontuar_senha("aaaB1!ccc") == 18 + 60 - 20
        assert pontuar_senha("aaaBBB111!!!") == 24 + 60 - 40

    def test_limitacao_ao_intervalo_0_a_100(self):
        # Abaixo de 0 é limitado a 0
        assert pontuar_senha("...") == 0  # 6 + 0 - 10 = -4 -> 0
        assert pontuar_senha("...+") == 0  # 8 + 0 - 10 = -2 -> 0
        assert pontuar_senha("aaaaa") == 0  # 10 + 15 - 30 = -5 -> 0
        assert pontuar_senha("aaaaa.+") == 0  # 14 + 15 - 30 = -1 -> 0
        # Exatamente 0 sem precisar truncar
        assert pontuar_senha("") == 0
        assert pontuar_senha("...+.") == 0  # 10 + 0 - 10 = 0
        # Exatamente 1
        assert pontuar_senha("aaaaa.+.") == 1  # 16 + 15 - 30 = 1
        # Exatamente 2
        assert pontuar_senha(".") == 2
        assert pontuar_senha("...+.+") == 2  # 12 + 0 - 10 = 2
        # Limite superior 100
        assert pontuar_senha("Abcdefghij123456789!") == 100
        assert pontuar_senha("Abcdefghij123456789!xyzXYZ") == 100


class TestClassificar:
    @pytest.mark.parametrize("espaco", [" ", "\t", "\n", "\r", "\v", "\f", "\u00a0"])
    def test_com_espaco_retorna_invalida_independente_da_pontuacao(self, espaco):
        # Pontuação baixa (< 50)
        assert classificar(espaco) == "invalida"
        assert classificar(f"abc{espaco}") == "invalida"
        # Pontuação média (50..79)
        assert classificar(f"Abcdef1!{espaco}") == "invalida"
        # Pontuação alta (>= 80 / 100)
        assert classificar(f"Abcdefghij123456789!{espaco}") == "invalida"

    def test_outros_problemas_de_validacao_sem_espaco_nao_retornam_invalida(self):
        # "curta", mas pontuação 68 -> "media"
        assert validar_senha("Ab1!") == ["curta"]
        assert pontuar_senha("Ab1!") == 68
        assert classificar("Ab1!") == "media"

        # "sem_maiuscula", mas pontuação 85 -> "forte"
        s_sem_maius = "abcdefghij1234567890!"
        assert validar_senha(s_sem_maius) == ["sem_maiuscula"]
        assert pontuar_senha(s_sem_maius) == 85
        assert classificar(s_sem_maius) == "forte"

        # "sem_minuscula", mas pontuação 85 -> "forte"
        s_sem_minus = "ABCDEFGHIJ1234567890!"
        assert validar_senha(s_sem_minus) == ["sem_minuscula"]
        assert pontuar_senha(s_sem_minus) == 85
        assert classificar(s_sem_minus) == "forte"

        # "sem_digito", mas pontuação 85 -> "forte"
        s_sem_dig = "Abcdefghijklmnopqrst!"
        assert validar_senha(s_sem_dig) == ["sem_digito"]
        assert pontuar_senha(s_sem_dig) == 85
        assert classificar(s_sem_dig) == "forte"

        # "sem_especial", mas pontuação 85 -> "forte"
        s_sem_esp = "Abcdefghij1234567890"
        assert validar_senha(s_sem_esp) == ["sem_especial"]
        assert pontuar_senha(s_sem_esp) == 85
        assert classificar(s_sem_esp) == "forte"

        # Senha sem problemas em validar_senha, mas com trincas -> pontuação 46 -> "fraca"
        s_valida_fraca = "Aaaaaa1!"
        assert validar_senha(s_valida_fraca) == []
        assert pontuar_senha(s_valida_fraca) == 46
        assert classificar(s_valida_fraca) == "fraca"

    def test_fronteiras_exatas_de_pontuacao(self):
        # 0 pontos -> "fraca"
        assert pontuar_senha("") == 0
        assert classificar("") == "fraca"

        # 48 pontos -> "fraca"
        s48 = "Abcdefghi"  # len 9 (18) + 2 cats (30) = 48
        assert pontuar_senha(s48) == 48
        assert classificar(s48) == "fraca"

        # 49 pontos -> "fraca"
        s49 = "Aaaa1bc"  # len 7 (14) + 3 cats (45) - 1 trinca (10) = 49
        assert pontuar_senha(s49) == 49
        assert classificar(s49) == "fraca"

        # 50 pontos -> "media"
        s50 = "Abcdefghij"  # len 10 (20) + 2 cats (30) = 50
        assert pontuar_senha(s50) == 50
        assert classificar(s50) == "media"

        # 51 pontos -> "media"
        s51 = "Aa1"  # len 3 (6) + 3 cats (45) = 51
        assert pontuar_senha(s51) == 51
        assert classificar(s51) == "media"

        # 78 pontos -> "media"
        s78 = "Abcdef1!g"  # len 9 (18) + 4 cats (60) = 78
        assert pontuar_senha(s78) == 78
        assert classificar(s78) == "media"

        # 79 pontos -> "media"
        s79 = "Abcdefghijklmno12"  # len 17 (34) + 3 cats (45) = 79
        assert pontuar_senha(s79) == 79
        assert classificar(s79) == "media"

        # 80 pontos -> "forte"
        s80 = "Abcdefgh1!"  # len 10 (20) + 4 cats (60) = 80
        assert pontuar_senha(s80) == 80
        assert classificar(s80) == "forte"

        # 81 pontos -> "forte"
        s81 = "Abcdefghijklmnop12"  # len 18 (36) + 3 cats (45) = 81
        assert pontuar_senha(s81) == 81
        assert classificar(s81) == "forte"

        # 100 pontos -> "forte"
        s100 = "Abcdefghij123456789!"  # len 20 (40) + 4 cats (60) = 100
        assert pontuar_senha(s100) == 100
        assert classificar(s100) == "forte"

    def test_classificar_tipo_invalido_levanta_type_error(self):
        with pytest.raises(TypeError):
            classificar(None)  # type: ignore[arg-type]
        with pytest.raises(TypeError):
            classificar(123)  # type: ignore[arg-type]
