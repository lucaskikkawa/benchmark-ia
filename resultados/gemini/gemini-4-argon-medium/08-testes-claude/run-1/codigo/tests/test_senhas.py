import pytest
from senhas import ESPECIAIS, classificar, pontuar_senha, validar_senha


class TestEspeciais:
    def test_tipo_e_conteudo(self):
        assert isinstance(ESPECIAIS, frozenset)
        assert ESPECIAIS == frozenset("!@#$%&*?-_")
        assert len(ESPECIAIS) == 10


class TestValidarSenhaExcecoes:
    @pytest.mark.parametrize("entrada_invalida", [None, 123, 12.5, ["a"], ("a",), b"Aa1!Aa1!", {"a": 1}])
    def test_senha_nao_str_levanta_type_error(self, entrada_invalida):
        with pytest.raises(TypeError):
            validar_senha(entrada_invalida)

    def test_senha_nao_str_com_tamanho_invalido_prioriza_type_error(self):
        with pytest.raises(TypeError):
            validar_senha(None, 0)

    @pytest.mark.parametrize("tamanho", [0, -1, -2, -100])
    def test_tamanho_minimo_menor_que_1_levanta_value_error(self, tamanho):
        with pytest.raises(ValueError):
            validar_senha("Aa1!Bb2@", tamanho_minimo=tamanho)


class TestValidarSenhaRegras:
    def test_senha_valida_padrao(self):
        assert validar_senha("Aa1!Bb2@") == []

    def test_tamanho_minimo_padrao_borda(self):
        assert validar_senha("Aa1!Bb2") == ["curta"]
        assert validar_senha("Aa1!Bb2@") == []
        assert validar_senha("Aa1!Bb2@C") == []

    @pytest.mark.parametrize("tam", [1, 2, 5, 8, 10, 15])
    def test_tamanho_minimo_customizado_borda(self, tam):
        base = "Aa1!Bb2@Cc3#Dd4$Ee5%"
        # Para tam >= 4 podemos usar uma senha com todas as categorias
        if tam >= 4:
            senha_exata = base[:tam]
            senha_curta = base[: tam - 1]
            assert "curta" not in validar_senha(senha_exata, tam)
            assert "curta" in validar_senha(senha_curta, tam)
        else:
            assert "curta" not in validar_senha("a" * tam, tam)
            assert "curta" in validar_senha("a" * (tam - 1), tam)

    def test_tamanho_minimo_1_string_vazia_e_1_char(self):
        assert "curta" in validar_senha("", 1)
        assert "curta" not in validar_senha("a", 1)

    def test_ordem_completa_dos_problemas(self):
        assert validar_senha("") == [
            "curta",
            "sem_maiuscula",
            "sem_minuscula",
            "sem_digito",
            "sem_especial",
        ]
        assert validar_senha("   ") == [
            "curta",
            "sem_maiuscula",
            "sem_minuscula",
            "sem_digito",
            "sem_especial",
            "espaco",
        ]

    def test_cada_problema_isoladamente(self):
        assert validar_senha("Aa1!Bb2") == ["curta"]
        assert validar_senha("aa1!bb2@") == ["sem_maiuscula"]
        assert validar_senha("AA1!BB2@") == ["sem_minuscula"]
        assert validar_senha("Aa!@Bb#$") == ["sem_digito"]
        assert validar_senha("Aa12Bb34") == ["sem_especial"]
        assert validar_senha("Aa1! Bb2@") == ["espaco"]

    def test_unicidade_dos_codigos(self):
        res = validar_senha("  ")
        assert res == [
            "curta",
            "sem_maiuscula",
            "sem_minuscula",
            "sem_digito",
            "sem_especial",
            "espaco",
        ]
        assert len(res) == len(set(res))

    @pytest.mark.parametrize("digito", list("0123456789"))
    def test_cada_digito_individualmente_satisfaz_regra(self, digito):
        senha = f"Aa!@Bb#{digito}"
        assert validar_senha(senha) == []

    @pytest.mark.parametrize("char_nao_ascii_digito", ["²", "³", "¹", "٠", "߀"])
    def test_digito_unicode_nao_conta_como_0_a_9(self, char_nao_ascii_digito):
        senha = f"Aa!@Bb#{char_nao_ascii_digito}"
        assert validar_senha(senha) == ["sem_digito"]

    @pytest.mark.parametrize("especial", list("!@#$%&*?-_"))
    def test_cada_especial_individualmente_satisfaz_regra(self, especial):
        senha = f"Aa12Bb3{especial}"
        assert validar_senha(senha) == []

    @pytest.mark.parametrize("nao_especial", list(".,;:+=/\\^~()[]{}<>\"'`|"))
    def test_outros_simbolos_nao_contam_como_especial(self, nao_especial):
        senha = f"Aa12Bb3{nao_especial}"
        assert validar_senha(senha) == ["sem_especial"]

    @pytest.mark.parametrize("maiuscula", ["A", "M", "Z", "Á", "Ç", "Õ"])
    def test_maiusculas_ascii_e_unicode(self, maiuscula):
        senha = f"{maiuscula}a1!bb2@"
        assert validar_senha(senha) == []

    @pytest.mark.parametrize("minuscula", ["a", "m", "z", "á", "ç", "õ"])
    def test_minusculas_ascii_e_unicode(self, minuscula):
        senha = f"A{minuscula}1!BB2@"
        assert validar_senha(senha) == []

    @pytest.mark.parametrize("espaco", [" ", "\t", "\n", "\r", "\v", "\f", "\u00a0"])
    def test_varios_tipos_de_espaco(self, espaco):
        assert validar_senha(f"Aa1!Bb2@{espaco}") == ["espaco"]
        assert validar_senha(f"{espaco}Aa1!Bb2@") == ["espaco"]
        assert validar_senha(f"Aa1!{espaco}Bb2@") == ["espaco"]


class TestPontuarSenha:
    def test_senha_vazia(self):
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
    def test_pontos_por_comprimento_sem_categorias_nem_trincas(self, tamanho, esperado):
        # '.' e '+' não pertencem a nenhuma das 4 categorias e alternados não formam trincas
        padrao = (".+" * ((tamanho // 2) + 1))[:tamanho]
        assert pontuar_senha(padrao) == esperado

    def test_pontos_por_cada_categoria_individual(self):
        assert pontuar_senha("A") == 2 + 15
        assert pontuar_senha("a") == 2 + 15
        assert pontuar_senha("5") == 2 + 15
        assert pontuar_senha("!") == 2 + 15

    @pytest.mark.parametrize("digito", list("0123456789"))
    def test_pontuar_cada_digito(self, digito):
        assert pontuar_senha(digito) == 17

    @pytest.mark.parametrize("char_nao_ascii_digito", ["²", "³", "¹"])
    def test_pontuar_digito_unicode_nao_ganha_categoria(self, char_nao_ascii_digito):
        assert pontuar_senha(char_nao_ascii_digito) == 2

    @pytest.mark.parametrize("especial", list("!@#$%&*?-_"))
    def test_pontuar_cada_especial(self, especial):
        assert pontuar_senha(especial) == 17

    @pytest.mark.parametrize("nao_especial", list(".,;:+=/\\^~()[]{}<>\"'`|"))
    def test_pontuar_simbolo_nao_especial_nao_ganha_categoria(self, nao_especial):
        assert pontuar_senha(nao_especial) == 2

    def test_combinacoes_de_categorias(self):
        assert pontuar_senha("Aa") == 4 + 30
        assert pontuar_senha("A1") == 4 + 30
        assert pontuar_senha("A!") == 4 + 30
        assert pontuar_senha("a1") == 4 + 30
        assert pontuar_senha("a!") == 4 + 30
        assert pontuar_senha("1!") == 4 + 30
        assert pontuar_senha("Aa1") == 6 + 45
        assert pontuar_senha("Aa!") == 6 + 45
        assert pontuar_senha("A1!") == 6 + 45
        assert pontuar_senha("a1!") == 6 + 45
        assert pontuar_senha("Aa1!") == 8 + 60

    def test_trincas_janela_deslizante(self):
        # Dupla não penaliza
        assert pontuar_senha("aa") == 4 + 15
        assert pontuar_senha("Aa1!aa") == 12 + 60
        # 1 trinca ("aaa"): len=3 -> 6 + 15 - 10 = 11
        assert pontuar_senha("aaa") == 11
        # 2 trincas ("aaaa"): len=4 -> 8 + 15 - 20 = 3
        assert pontuar_senha("aaaa") == 3
        # Com base alta para verificar valores exatos sem bater no piso 0
        assert pontuar_senha("Aa1!aaa") == 14 + 60 - 10  # 64
        assert pontuar_senha("Aa1!aaaa") == 16 + 60 - 20  # 56
        assert pontuar_senha("Aa1!aaaaa") == 18 + 60 - 30  # 48
        assert pontuar_senha("Aa1!aaaaaa") == 20 + 60 - 40  # 40
        # Trincas no início, meio e múltiplas trincas distintas
        assert pontuar_senha("aaaAa1!") == 14 + 60 - 10  # 64
        assert pontuar_senha("Aa1aaa!") == 14 + 60 - 10  # 64
        assert pontuar_senha("Aa1!aaabbb") == 20 + 60 - 20  # 60

    def test_trincas_diferenciam_maiusculas_e_minusculas_e_nao_consecutivas(self):
        assert pontuar_senha("Aaa") == 6 + 30
        assert pontuar_senha("aAa") == 6 + 30
        assert pontuar_senha("aaA") == 6 + 30
        assert pontuar_senha("aba") == 6 + 15

    def test_limitacao_inferior_zero(self):
        # Raw score < 0 limitado a 0
        assert pontuar_senha("...") == 0  # 6 - 10 = -4 -> 0
        assert pontuar_senha("aaaaa") == 0  # 10 + 15 - 30 = -5 -> 0
        assert pontuar_senha("a.....b") == 0  # 14 + 15 - 30 = -1 -> 0
        # Raw score == 0 e == 1
        assert pontuar_senha(".+...") == 0  # 10 + 0 - 10 = 0
        assert pontuar_senha("a.....bc") == 1  # 16 + 15 - 30 = 1

    def test_limitacao_superior_cem(self):
        # 19 chars + 4 categorias = 38 + 60 = 98
        assert pontuar_senha("Aa1!Bb2@Cc3#Dd4$Ee5") == 98
        # 20 chars + 4 categorias = 40 + 60 = 100
        assert pontuar_senha("Aa1!Bb2@Cc3#Dd4$Ee5%") == 100
        # > 20 chars + 4 categorias continua 100
        assert pontuar_senha("Aa1!Bb2@Cc3#Dd4$Ee5%Ff6&Gg7*") == 100


class TestClassificar:
    @pytest.mark.parametrize("espaco", [" ", "\t", "\n", "\r", "\v", "\f"])
    def test_senha_com_espaco_sempre_invalida(self, espaco):
        assert classificar(espaco) == "invalida"
        assert classificar(f"abc{espaco}") == "invalida"
        assert classificar(f"Aa1!Bb2@{espaco}") == "invalida"
        assert classificar(f"Aa1!Bb2@Cc3#Dd4$Ee5%{espaco}") == "invalida"

    def test_senha_nao_str_levanta_type_error(self):
        with pytest.raises(TypeError):
            classificar(None)  # type: ignore[arg-type]

    def test_fronteira_fraca_e_media_em_50(self):
        # 0 pontos -> fraca
        assert pontuar_senha("") == 0
        assert classificar("") == "fraca"
        # 48 pontos -> fraca
        assert pontuar_senha("Aaabababa") == 48
        assert classificar("Aaabababa") == "fraca"
        # 49 pontos -> fraca
        assert pontuar_senha("Aa1...a") == 49
        assert classificar("Aa1...a") == "fraca"
        # 50 pontos -> media
        assert pontuar_senha("Ababababab") == 50
        assert classificar("Ababababab") == "media"
        # 51 pontos -> media
        assert pontuar_senha("Aa1") == 51
        assert classificar("Aa1") == "media"

    def test_fronteira_media_e_forte_em_80(self):
        # 78 pontos -> media
        assert pontuar_senha("Aa1!Bb2@C") == 78
        assert classificar("Aa1!Bb2@C") == "media"
        # 79 pontos -> media
        assert pontuar_senha("Aa1Bb2Cc3Dd4Ee5Ff") == 79
        assert classificar("Aa1Bb2Cc3Dd4Ee5Ff") == "media"
        # 80 pontos -> forte
        assert pontuar_senha("Aa1!Bb2@Cc") == 80
        assert classificar("Aa1!Bb2@Cc") == "forte"
        # 81 pontos -> forte
        assert pontuar_senha("Aa1Bb2Cc3Dd4Ee5Ff6") == 81
        assert classificar("Aa1Bb2Cc3Dd4Ee5Ff6") == "forte"
        # 100 pontos -> forte
        assert pontuar_senha("Aa1!Bb2@Cc3#Dd4$Ee5%") == 100
        assert classificar("Aa1!Bb2@Cc3#Dd4$Ee5%") == "forte"

    def test_outros_problemas_de_validacao_nao_tornam_invalida(self):
        # Curta (len 4 < 8), mas sem espaço -> classificada pelos pontos (68 -> media)
        assert "curta" in validar_senha("Aa1!")
        assert classificar("Aa1!") == "media"
        # Sem especial, mas pontuação 81 -> forte
        assert validar_senha("Aa1Bb2Cc3Dd4Ee5Ff6") == ["sem_especial"]
        assert classificar("Aa1Bb2Cc3Dd4Ee5Ff6") == "forte"
