"""Suíte de testes para o módulo senhas."""

import pytest

from senhas import ESPECIAIS, classificar, pontuar_senha, validar_senha


# ---------------------------------------------------------------------------
# Constante ESPECIAIS
# ---------------------------------------------------------------------------


class TestEspeciais:
    def test_tipo_e_conteudo_exato(self):
        assert isinstance(ESPECIAIS, frozenset)
        assert ESPECIAIS == frozenset("!@#$%&*?-_")
        assert len(ESPECIAIS) == 10

    @pytest.mark.parametrize("char", list("^()+=.,;:/\\~`'\"[]{}<>| \t\n0aA"))
    def test_caracteres_fora_de_especiais(self, char):
        assert char not in ESPECIAIS


# ---------------------------------------------------------------------------
# validar_senha
# ---------------------------------------------------------------------------


class TestValidarSenha:
    def test_senha_valida_padrao(self):
        assert validar_senha("Abcd123!") == []
        assert isinstance(validar_senha("Abcd123!"), list)

    def test_erros_de_tipo_para_senha(self):
        for invalido in (None, 12345678, 12.34, True, b"Abcd123!", ["Abcd123!"], {"s": "Abcd123!"}):
            with pytest.raises(TypeError):
                validar_senha(invalido)

    @pytest.mark.parametrize("tamanho", [0, -1, -8, -100])
    def test_erros_de_valor_para_tamanho_minimo(self, tamanho):
        with pytest.raises(ValueError):
            validar_senha("Abcd123!", tamanho_minimo=tamanho)

    def test_tamanho_minimo_um_e_valido(self):
        assert "curta" not in validar_senha("a", tamanho_minimo=1)
        assert "curta" in validar_senha("", tamanho_minimo=1)

    @pytest.mark.parametrize(
        ("senha", "tamanho_minimo", "espera_curta"),
        [
            ("Ab1!xyz", 8, True),   # 7 < 8
            ("Ab1!wxyz", 8, False),  # 8 == 8 (borda)
            ("Ab1!vwxyz", 8, False),  # 9 > 8
            ("Ab1!", 4, False),
            ("Ab1", 4, True),
            ("Ab1!5678901", 12, True),
            ("Ab1!56789012", 12, False),
        ],
    )
    def test_borda_tamanho_minimo(self, senha, tamanho_minimo, espera_curta):
        problemas = validar_senha(senha, tamanho_minimo=tamanho_minimo)
        assert ("curta" in problemas) is espera_curta

    def test_tamanho_minimo_padrao_e_8(self):
        assert validar_senha("Ab1!567") == ["curta"]
        assert validar_senha("Ab1!5678") == []

    def test_tamanho_conta_espacos(self):
        # len == 8, mas len(strip()) == 4: não deve ser "curta", apenas "espaco"
        assert validar_senha("Ab1!    ") == ["espaco"]
        assert validar_senha("    Ab1!") == ["espaco"]

    def test_cada_problema_isoladamente(self):
        assert validar_senha("Ab1!567") == ["curta"]
        assert validar_senha("abcdef1!") == ["sem_maiuscula"]
        assert validar_senha("ABCDEF1!") == ["sem_minuscula"]
        assert validar_senha("Abcdefg!") == ["sem_digito"]
        assert validar_senha("Abcdefg1") == ["sem_especial"]
        assert validar_senha("Abcdef1! ") == ["espaco"]

    def test_todos_os_problemas_em_ordem_e_sem_duplicatas(self):
        # Múltiplos espaços, curta, sem nenhuma das 4 categorias
        assert validar_senha("   ") == [
            "curta",
            "sem_maiuscula",
            "sem_minuscula",
            "sem_digito",
            "sem_especial",
            "espaco",
        ]

    def test_string_vazia(self):
        assert validar_senha("") == [
            "curta",
            "sem_maiuscula",
            "sem_minuscula",
            "sem_digito",
            "sem_especial",
        ]

    @pytest.mark.parametrize(
        ("senha", "esperado"),
        [
            ("abc1!xy", ["curta", "sem_maiuscula"]),
            ("1234567!", ["sem_maiuscula", "sem_minuscula"]),
            ("ABCDEFG!", ["sem_minuscula", "sem_digito"]),
            ("Abcdefgh", ["sem_digito", "sem_especial"]),
            ("Abcdef1 ", ["sem_especial", "espaco"]),
            ("abc 1", ["curta", "sem_maiuscula", "sem_especial", "espaco"]),
            ("A 1", ["curta", "sem_minuscula", "sem_especial", "espaco"]),
        ],
    )
    def test_ordem_de_multiplos_problemas(self, senha, esperado):
        assert validar_senha(senha) == esperado

    @pytest.mark.parametrize("char", sorted(ESPECIAIS))
    def test_cada_especial_valido_aceito(self, char):
        assert validar_senha(f"Abcdef1{char}") == []
        assert validar_senha(f"{char}Abcdef1") == []

    @pytest.mark.parametrize("char", list("^()+=.,;:/\\~`'\"[]{}<>|"))
    def test_pontuacao_fora_de_especiais_rejeitada(self, char):
        assert validar_senha(f"Abcdef1{char}") == ["sem_especial"]

    @pytest.mark.parametrize("digito", list("0123456789"))
    def test_cada_digito_ascii_aceito(self, digito):
        assert validar_senha(f"Abcdef!{digito}") == []
        assert validar_senha(f"{digito}Abcdef!") == []

    @pytest.mark.parametrize("nao_ascii_digito", ["²", "³", "٠", "٣", "０", "９", "½"])
    def test_digito_unicode_nao_conta_como_digito(self, nao_ascii_digito):
        assert validar_senha(f"Abcdef!{nao_ascii_digito}") == ["sem_digito"]

    @pytest.mark.parametrize("maiuscula", ["A", "Z", "Á", "Ç", "É", "Ñ", "Ü"])
    def test_maiuscula_ascii_e_unicode_em_posicoes_variadas(self, maiuscula):
        assert validar_senha(f"{maiuscula}bcdef1!") == []
        assert validar_senha(f"bcde{maiuscula}f1!") == []
        assert validar_senha(f"bcdef1!{maiuscula}") == []

    @pytest.mark.parametrize("minuscula", ["a", "z", "á", "ç", "é", "ñ", "ü"])
    def test_minuscula_ascii_e_unicode_em_posicoes_variadas(self, minuscula):
        assert validar_senha(f"{minuscula}BCDEF1!") == []
        assert validar_senha(f"BCDE{minuscula}F1!") == []
        assert validar_senha(f"BCDEF1!{minuscula}") == []

    @pytest.mark.parametrize("ws", [" ", "\t", "\n", "\r", "\v", "\f", "\u00a0", "\u3000"])
    def test_espacos_ascii_e_unicode_em_qualquer_posicao(self, ws):
        assert validar_senha(f"{ws}Abcdef1!") == ["espaco"]
        assert validar_senha(f"Abcd{ws}ef1!") == ["espaco"]
        assert validar_senha(f"Abcdef1!{ws}") == ["espaco"]

    def test_chamadas_retornam_listas_independentes(self):
        r1 = validar_senha("abc")
        r1.append("mutado")
        r2 = validar_senha("abc")
        assert "mutado" not in r2


# ---------------------------------------------------------------------------
# pontuar_senha
# ---------------------------------------------------------------------------


class TestPontuarSenha:
    def test_string_vazia(self):
        assert pontuar_senha("") == 0
        assert type(pontuar_senha("")) is int

    @pytest.mark.parametrize(
        ("senha", "esperado"),
        [
            ("+", 2),
            ("+=", 4),
            ("+=+=" * 2 + "+=", 20),       # len 10 -> 20
            ("+=" * 9 + "+", 38),         # len 19 -> 38
            ("+=" * 10, 40),              # len 20 -> 40 (limite)
            ("+=" * 10 + "+", 40),        # len 21 -> ainda 40
            ("+=" * 15, 40),              # len 30 -> ainda 40
        ],
    )
    def test_pontos_por_comprimento_e_teto_20(self, senha, esperado):
        assert pontuar_senha(senha) == esperado

    def test_cada_categoria_vale_15_uma_unica_vez(self):
        # 1 caractere: 2 + 15 = 17
        assert pontuar_senha("A") == 17
        assert pontuar_senha("a") == 17
        assert pontuar_senha("0") == 17
        assert pontuar_senha("9") == 17
        assert pontuar_senha("!") == 17

        # 2 caracteres da mesma categoria: 4 + 15 = 19 (não +30)
        assert pontuar_senha("AB") == 19
        assert pontuar_senha("ab") == 19
        assert pontuar_senha("09") == 19
        assert pontuar_senha("!@") == 19

    def test_combinacoes_de_categorias(self):
        assert pontuar_senha("Aa") == 4 + 30
        assert pontuar_senha("Aa1") == 6 + 45
        assert pontuar_senha("Aa1!") == 8 + 60
        assert pontuar_senha("Aa1!" + "+=" * 8) == 40 + 60

    @pytest.mark.parametrize("char", sorted(ESPECIAIS))
    def test_todos_especiais_pontuam_categoria(self, char):
        assert pontuar_senha(char) == 17

    @pytest.mark.parametrize("char", list("^()+=.,;:/\\~`'\"[]{}<>| "))
    def test_nao_especiais_nao_pontuam_categoria(self, char):
        assert pontuar_senha(char) == 2

    @pytest.mark.parametrize("digito", list("0123456789"))
    def test_todos_digitos_ascii_pontuam_categoria(self, digito):
        assert pontuar_senha(digito) == 17

    @pytest.mark.parametrize("nao_ascii_digito", ["²", "٠", "０", "½"])
    def test_digito_unicode_nao_pontua_categoria(self, nao_ascii_digito):
        assert pontuar_senha(nao_ascii_digito) == 2

    def test_maiuscula_e_minuscula_unicode_pontuam_categoria(self):
        assert pontuar_senha("Á") == 17
        assert pontuar_senha("á") == 17
        assert pontuar_senha("Áá") == 4 + 30

    def test_espaco_conta_no_comprimento_mas_nao_e_categoria(self):
        assert pontuar_senha(" ") == 2
        assert pontuar_senha(" a") == 4 + 15

    def test_penalidade_de_trincas_janela_deslizante(self):
        # Sem trinca (dupla não penaliza)
        assert pontuar_senha("aa") == 4 + 15
        assert pontuar_senha("Aa1!aa") == 12 + 60
        # 1 trinca: -10
        assert pontuar_senha("aaa") == 6 + 15 - 10
        assert pontuar_senha("Aa1!aaa") == 14 + 60 - 10
        # 2 trincas ("aaaa" em janela deslizante): -20
        assert pontuar_senha("aaaa") == 8 + 15 - 20
        assert pontuar_senha("Aa1!aaaa") == 16 + 60 - 20
        # 3 trincas ("aaaaa" em janela deslizante): -30
        assert pontuar_senha("Aa1!aaaaa") == 18 + 60 - 30
        # 4 trincas ("aaaaaa"): -40
        assert pontuar_senha("Aa1!aaaaaa") == 20 + 60 - 40

    def test_trincas_em_inicio_meio_fim_e_multiplas_separadas(self):
        assert pontuar_senha("aaaB1!") == 12 + 60 - 10
        assert pontuar_senha("B1aaa!") == 12 + 60 - 10
        assert pontuar_senha("B1!aaa") == 12 + 60 - 10
        assert pontuar_senha("Aa1!xxxyyy") == 20 + 60 - 20
        assert pontuar_senha("Aa1!111!!!") == 20 + 60 - 20
        assert pontuar_senha("Aa1!   ") == 14 + 60 - 10

    def test_trincas_sao_sensiveis_a_maiusculas_e_minusculas(self):
        assert pontuar_senha("AaA") == 6 + 30
        assert pontuar_senha("aAa") == 6 + 30
        assert pontuar_senha("AAa") == 6 + 30

    def test_categorias_e_trincas_apos_20_caracteres(self):
        # Categoria presente apenas no 21º caractere
        assert pontuar_senha("+=" * 10 + "A") == 40 + 15
        # Trinca após os 20 primeiros caracteres ainda penaliza
        assert pontuar_senha("+=" * 10 + "aaa") == 40 + 15 - 10
        # Comprimento limitado a 20 ANTES da subtração da trinca: 40 + 60 - 10 = 90
        assert pontuar_senha("Ab1!" + "+=" * 8 + "aaa") == 90

    def test_limite_inferior_zero(self):
        # 10 + 15 - 30 = -5 -> 0
        assert pontuar_senha("aaaaa") == 0
        # 20 + 15 - 80 = -45 -> 0
        assert pontuar_senha("a" * 10) == 0
        # Sem categorias e com trincas
        assert pontuar_senha("+" * 10) == 0

    def test_limite_superior_cem(self):
        assert pontuar_senha("Ab1!" * 5) == 100
        assert pontuar_senha("Ab1!" * 10) == 100


# ---------------------------------------------------------------------------
# classificar
# ---------------------------------------------------------------------------


class TestClassificar:
    @pytest.mark.parametrize("ws", [" ", "\t", "\n", "\r", "\u00a0"])
    def test_espaco_retorna_invalida_independente_da_pontuacao(self, ws):
        # Pontuação baixa
        assert classificar(ws) == "invalida"
        # Pontuação média
        assert classificar(f"Aa1!{ws}") == "invalida"
        # Pontuação alta (>= 80)
        assert classificar(f"Abcdefgh12345678!{ws}") == "invalida"

    def test_outros_problemas_de_validacao_nao_tornam_invalida(self):
        # Curta (len 4), mas sem espaço: pontos = 8 + 60 = 68 -> "media"
        assert classificar("Aa1!") == "media"
        # Sem especial, mas 20 chars e 3 categorias: pontos = 40 + 45 = 85 -> "forte"
        assert classificar("Abcdefgh123456789012") == "forte"
        # String vazia: pontos = 0 -> "fraca"
        assert classificar("") == "fraca"

    def test_fronteiras_exatas_de_pontuacao(self):
        # 49 -> "fraca"
        s49 = "a" + "+=" * 8  # len 17 -> 34 + 15 = 49
        assert pontuar_senha(s49) == 49
        assert classificar(s49) == "fraca"

        # 50 -> "media"
        s50 = "Aa" + "+=" * 4  # len 10 -> 20 + 30 = 50
        assert pontuar_senha(s50) == 50
        assert classificar(s50) == "media"

        # 51 -> "media"
        s51 = "Aa1"  # len 3 -> 6 + 45 = 51
        assert pontuar_senha(s51) == 51
        assert classificar(s51) == "media"

        # 79 -> "media"
        s79 = "Aa1" + "+=" * 7  # len 17 -> 34 + 45 = 79
        assert pontuar_senha(s79) == 79
        assert classificar(s79) == "media"

        # 80 -> "forte"
        s80 = "Aa1!" + "+=" * 3  # len 10 -> 20 + 60 = 80
        assert pontuar_senha(s80) == 80
        assert classificar(s80) == "forte"

        # 81 -> "forte"
        s81 = "Aa1" + "+=" * 7 + "+"  # len 18 -> 36 + 45 = 81
        assert pontuar_senha(s81) == 81
        assert classificar(s81) == "forte"

        # 100 -> "forte"
        s100 = "Aa1!" + "+=" * 8  # len 20 -> 40 + 60 = 100
        assert pontuar_senha(s100) == 100
        assert classificar(s100) == "forte"

    def test_classificar_com_trincas_reduzindo_faixa(self):
        # Sem trinca seria 40 + 60 = 100 ("forte"); com 3 trincas: 100 - 30 = 70 ("media")
        s_media = "Ab1!" + "+=" * 6 + "aaaaa"  # len 21 -> 40 + 60 - 30 = 70
        assert pontuar_senha(s_media) == 70
        assert classificar(s_media) == "media"

        # Com 6 trincas: 40 + 60 - 60 = 40 ("fraca")
        s_fraca = "Ab1!" + "+=" * 4 + "aaaaaaaa"  # len 20 -> 40 + 60 - 60 = 40
        assert pontuar_senha(s_fraca) == 40
        assert classificar(s_fraca) == "fraca"

    def test_classificar_propaga_type_error(self):
        with pytest.raises(TypeError):
            classificar(None)
        with pytest.raises(TypeError):
            classificar(12345678)
