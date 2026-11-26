import pytest

from carrinho import calcular_total


class TestCalculoBasicoEContrato:
    def test_carrinho_vazio_sem_opcionais(self):
        res = calcular_total([])
        assert type(res) is int
        assert res == 0

    @pytest.mark.parametrize(
        ("desconto", "frete"),
        [
            (0, 0),
            (0, 500),
            (10, 0),
            (10, 500),
            (100, 0),
            (100, 500),
        ],
    )
    def test_carrinho_vazio_nunca_cobra_frete(self, desconto, frete):
        res = calcular_total([], desconto=desconto, frete=frete)
        assert type(res) is int
        assert res == 0

    def test_argumentos_padrao_posicionais_e_nomeados(self):
        itens = [(2, 350)]
        assert calcular_total(itens) == 700
        assert calcular_total(itens, 10) == 630
        assert calcular_total(itens, 10, 200) == 830
        assert calcular_total(itens, frete=200) == 900
        assert calcular_total(itens=itens, desconto=10, frete=200) == 830

    def test_varios_itens_e_linhas_duplicadas(self):
        res = calcular_total([(2, 150), (3, 400), (1, 50)])
        assert type(res) is int
        assert res == 1550

        # Linhas duplicadas devem ser somadas, nunca deduplicadas.
        assert calcular_total([(1, 100), (1, 100)]) == 200
        assert calcular_total([(2, 250), (2, 250), (2, 250)]) == 1500

    def test_ordem_dos_itens_nao_altera_total(self):
        a = [(1, 130), (3, 250), (0, 999), (2, 0)]
        b = [(2, 0), (0, 999), (3, 250), (1, 130)]
        assert calcular_total(a, desconto=15, frete=300) == 1048
        assert calcular_total(b, desconto=15, frete=300) == 1048


class TestDescontoETruncamento:
    @pytest.mark.parametrize(
        ("itens", "desconto", "esperado"),
        [
            ([(1, 1000)], 0, 1000),
            ([(1, 1000)], 1, 990),
            ([(1, 100)], 7, 93),  # 100 * (1 - 7/100) em float resulta em 92.99999999999999
            ([(1, 1000)], 10, 900),
            ([(1, 1000)], 25, 750),
            ([(1, 1000)], 50, 500),
            ([(1, 1000)], 99, 10),
            ([(1, 1000)], 100, 0),
        ],
    )
    def test_percentuais_exatos_e_bordas(self, itens, desconto, esperado):
        res = calcular_total(itens, desconto=desconto)
        assert type(res) is int
        assert res == esperado

    @pytest.mark.parametrize(
        ("itens", "desconto", "esperado"),
        [
            # 101 * 99 / 100 = 99.99 -> floor 99 (round/ceil/bruto - floor(desc) dariam 100)
            ([(1, 101)], 1, 99),
            # 101 * 1 / 100 = 1.01 -> floor 1 (ceil/bruto - floor(desc) dariam 2)
            ([(1, 101)], 99, 1),
            # 3 * 50 / 100 = 1.5 -> floor 1 (round/half-up dariam 2)
            ([(1, 3)], 50, 1),
            # 5 * 50 / 100 = 2.5 -> floor 2 (half-up daria 3)
            ([(1, 5)], 50, 2),
            # 7 * 50 / 100 = 3.5 -> floor 3 (round/half-up dariam 4)
            ([(1, 7)], 50, 3),
            # 199 * 90 / 100 = 179.1 -> floor 179 (ceil/bruto - floor(desc) dariam 180)
            ([(1, 199)], 10, 179),
            # 1 * 99 / 100 = 0.99 -> floor 0
            ([(1, 1)], 1, 0),
        ],
    )
    def test_truncamento_para_baixo(self, itens, desconto, esperado):
        res = calcular_total(itens, desconto=desconto)
        assert type(res) is int
        assert res == esperado

    @pytest.mark.parametrize(
        ("itens", "desconto", "esperado"),
        [
            # Bruto 6, 50% -> 3; por linha seria 1 + 1 = 2
            ([(1, 3), (1, 3)], 50, 3),
            # Bruto 6, 50% -> 3; por unidade seria 2 * 1 = 2
            ([(2, 3)], 50, 3),
            # Bruto 10, 10% -> 9; por linha seria 4 + 4 = 8
            ([(1, 5), (1, 5)], 10, 9),
            # Bruto 33, 10% -> 29; por linha seria 9 + 9 + 9 = 27
            ([(1, 11), (1, 11), (1, 11)], 10, 29),
            # Bruto 3, 34% -> 3 * 66 // 100 = 1; por linha seria 0 + 0 + 0 = 0
            ([(1, 1), (1, 1), (1, 1)], 34, 1),
            # Bruto 91, 15% -> 91 * 85 // 100 = 77; por linha seria 48 + 28 = 76
            ([(3, 19), (2, 17)], 15, 77),
        ],
    )
    def test_truncamento_agregado_entre_linhas_e_unidades(self, itens, desconto, esperado):
        res = calcular_total(itens, desconto=desconto)
        assert type(res) is int
        assert res == esperado


class TestRegrasDeFrete:
    def test_frete_nao_recebe_desconto(self):
        assert calcular_total([(1, 1000)], desconto=50, frete=200) == 700
        assert calcular_total([(1, 1000)], desconto=100, frete=500) == 500
        assert calcular_total([(1, 101)], desconto=1, frete=100) == 199

    def test_frete_cobrado_uma_unica_vez_por_carrinho(self):
        assert calcular_total([(1, 100)], frete=500) == 600
        assert calcular_total([(3, 100), (2, 200)], frete=500) == 1200
        assert calcular_total([(1, 100)], frete=0) == 100
        assert calcular_total([(1, 100)], frete=1) == 101

    def test_item_gratuito_com_quantidade_positiva_paga_frete(self):
        assert calcular_total([(1, 0)], frete=500) == 500
        assert calcular_total([(3, 0)], desconto=20, frete=500) == 500
        assert calcular_total([(2, 0)], desconto=100, frete=500) == 500
        assert calcular_total([(1, 0)], frete=0) == 0

    def test_liquido_zero_por_truncamento_ainda_paga_frete(self):
        # 1 * 99 // 100 == 0, mas unidades == 1 > 0 -> cobra frete
        assert calcular_total([(1, 1)], desconto=1, frete=250) == 250

    def test_linhas_com_quantidade_zero_nao_pagam_frete(self):
        assert calcular_total([(0, 1000)], frete=500) == 0
        assert calcular_total([(0, 0)], frete=500) == 0
        assert calcular_total([(0, 100), (0, 200)], frete=500) == 0
        assert calcular_total([(0, 1000)], desconto=100, frete=500) == 0

    def test_mistura_quantidade_zero_e_positiva_em_qualquer_posicao(self):
        # Quantidade zero no início não interrompe o processamento.
        assert calcular_total([(0, 500), (2, 150)], frete=300) == 600
        assert calcular_total([(0, 500), (1, 0)], frete=300) == 300
        # Quantidade zero no final não zera as unidades acumuladas.
        assert calcular_total([(2, 150), (0, 500)], frete=300) == 600
        assert calcular_total([(1, 0), (0, 500)], frete=300) == 300


class TestPrecisaoArbitraria:
    def test_valores_acima_de_2_elevado_a_53_sem_desconto(self):
        grande = 2**53 + 1
        assert calcular_total([(1, grande)]) == 9007199254740993
        assert calcular_total([(grande, 1)]) == 9007199254740993
        assert calcular_total([(1, grande)], frete=2**53 + 5) == 18014398509481990

    def test_valores_acima_de_2_elevado_a_53_com_desconto(self):
        # Acima de 2**53, aritmética em float64 perde precisão nos bits menos significativos.
        p1 = 2**53 + 3  # 9007199254740995
        # 9007199254740995 * 99 = 891712726219358505 -> // 100 = 8917127262193585
        res1 = calcular_total([(1, p1)], desconto=1)
        assert type(res1) is int
        assert res1 == 8917127262193585

        # (2**53 + 3) * 50 // 100 = 4503599627370497; em float64 resulta em 4503599627370498
        res_half = calcular_total([(1, p1)], desconto=50)
        assert type(res_half) is int
        assert res_half == 4503599627370497

        p2 = 2**60 + 17  # 1152921504606846993
        # 1152921504606846993 * 87 = 100304170900795688391 -> // 100 = 1003041709007956883
        res2 = calcular_total([(1, p2)], desconto=13)
        assert type(res2) is int
        assert res2 == 1003041709007956883

        # Produto grande de quantidade * preço + frete grande
        q = 10**12 + 3
        p = 10**12 + 7
        # bruto = 1000000000010000000000021
        # bruto * 63 = 63000000000630000000001323 -> // 100 = 630000000006300000000013
        # + frete (10**18 + 9) = 630001000006300000000022
        res3 = calcular_total([(q, p)], desconto=37, frete=10**18 + 9)
        assert type(res3) is int
        assert res3 == 630001000006300000000022

    def test_inteiros_maiores_que_precisao_padrao_decimal(self):
        # 41 dígitos excede a precisão padrão de 28 dígitos de decimal.Decimal.
        p = 10**40 + 73
        # (10**40 + 73) * 93 = 93 * 10**40 + 6789 -> // 100 = 93 * 10**38 + 67
        esperado = 93 * 10**38 + 67 + (10**40 + 11)
        res = calcular_total([(1, p)], desconto=7, frete=10**40 + 11)
        assert type(res) is int
        assert res == esperado


class TestValidacoesEExcecoes:
    @pytest.mark.parametrize("desconto", [-100, -1, 101, 200])
    @pytest.mark.parametrize("itens", [[], [(0, 100)], [(1, 100)], [(2, 0)]])
    def test_desconto_fora_da_faixa_lanca_value_error(self, itens, desconto):
        with pytest.raises(ValueError):
            calcular_total(itens, desconto=desconto, frete=0)

    @pytest.mark.parametrize("frete", [-1, -500])
    @pytest.mark.parametrize(
        ("itens", "desconto"),
        [
            ([], 0),
            ([(0, 100)], 0),
            ([(1, 0)], 0),
            ([(1, 100)], 0),
            ([(1, 100)], 100),
        ],
    )
    def test_frete_negativo_lanca_value_error(self, itens, desconto, frete):
        with pytest.raises(ValueError):
            calcular_total(itens, desconto=desconto, frete=frete)

    @pytest.mark.parametrize(
        ("itens", "desconto"),
        [
            ([(-1, 100)], 0),
            ([(-1, 0)], 0),
            ([(5, 100), (-1, 100)], 0),
            ([(1, 100), (-1, 100)], 0),
            ([(-1, 100)], 100),
        ],
    )
    def test_quantidade_negativa_lanca_value_error(self, itens, desconto):
        with pytest.raises(ValueError):
            calcular_total(itens, desconto=desconto, frete=100)

    @pytest.mark.parametrize(
        ("itens", "desconto"),
        [
            ([(1, -1)], 0),
            ([(0, -1)], 0),
            ([(2, 100), (1, -50)], 0),
            ([(1, -100)], 100),
            ([(0, -1)], 100),
        ],
    )
    def test_preco_negativo_lanca_value_error(self, itens, desconto):
        with pytest.raises(ValueError):
            calcular_total(itens, desconto=desconto, frete=100)

    @pytest.mark.parametrize(
        "itens",
        [
            [(0, 100), (-1, 100)],
            [(0, 100), (1, -1)],
            [(0, 100), (0, -1)],
            [(0, 0), (0, 50), (-2, 10)],
            [(0, 0), (0, 50), (2, -10)],
        ],
    )
    def test_valida_linhas_posteriores_a_quantidade_zero(self, itens):
        with pytest.raises(ValueError):
            calcular_total(itens, desconto=0, frete=100)


class TestImutabilidadeEIndependencia:
    @pytest.mark.parametrize(
        "itens_inicial",
        [
            [],
            [(1, 100)],
            [(0, 100), (0, 200)],
            [(2, 300), (0, 100), (1, 50), (3, 0), (1, 50)],
        ],
    )
    def test_nao_altera_lista_em_chamada_valida(self, itens_inicial):
        itens = list(itens_inicial)
        copia = list(itens_inicial)
        calcular_total(itens, desconto=15, frete=250)
        assert itens == copia

    @pytest.mark.parametrize(
        ("itens_inicial", "desconto", "frete"),
        [
            ([], -1, 0),
            ([], 101, 0),
            ([], 0, -1),
            ([(2, 300), (0, 100)], -1, 250),
            ([(2, 300), (0, 100)], 101, 250),
            ([(2, 300), (0, 100)], 10, -1),
            ([(-1, 100), (2, 300)], 10, 250),
            ([(2, 300), (-1, 100), (1, 50)], 0, 0),
            ([(2, 300), (-1, 100), (1, 50)], 10, 250),
            ([(2, 300), (1, -50), (1, 50)], 0, 0),
            ([(2, 300), (1, -50), (1, 50)], 10, 250),
            ([(2, 300), (0, -1), (1, 50)], 10, 250),
            ([(2, 300), (0, 100), (-1, 50)], 10, 250),
            ([(2, 300), (0, 100), (1, -50)], 100, 250),
        ],
    )
    def test_nao_altera_lista_quando_lanca_value_error(self, itens_inicial, desconto, frete):
        itens = list(itens_inicial)
        copia = list(itens_inicial)
        with pytest.raises(ValueError):
            calcular_total(itens, desconto=desconto, frete=frete)
        assert itens == copia

    def test_chamadas_sao_independentes(self):
        itens = [(2, 500)]
        assert calcular_total(itens, desconto=0, frete=0) == 1000
        assert calcular_total(itens, desconto=10, frete=0) == 900
        assert calcular_total(itens, desconto=10, frete=200) == 1100
        assert calcular_total(itens, desconto=0, frete=200) == 1200
        assert calcular_total(itens, desconto=0, frete=0) == 1000
        assert calcular_total([], desconto=0, frete=500) == 0

        # Alteração feita pelo chamador entre chamadas deve refletir no próximo cálculo.
        itens.append((1, 200))
        assert calcular_total(itens, desconto=0, frete=0) == 1200

        # Carrinhos distintos de mesmo tamanho não compartilham resultado em cache.
        assert calcular_total([(1, 100)], desconto=10, frete=50) == 140
        assert calcular_total([(1, 200)], desconto=10, frete=50) == 230

    def test_preservacao_de_estado_apos_erros(self):
        assert calcular_total([(2, 100)], desconto=10, frete=50) == 230

        # Erro no meio do laço após acumular itens válidos.
        with pytest.raises(ValueError):
            calcular_total([(5, 1000), (-1, 100)], desconto=20, frete=300)
        assert calcular_total([], desconto=0, frete=500) == 0
        assert calcular_total([(0, 100)], desconto=0, frete=500) == 0
        assert calcular_total([(1, 100)], desconto=0, frete=0) == 100

        # Erro de preço negativo após itens válidos.
        with pytest.raises(ValueError):
            calcular_total([(3, 200), (1, -1)], desconto=50, frete=400)
        assert calcular_total([(1, 50)], frete=10) == 60
        assert calcular_total([(0, 100)], frete=10) == 0

        # Erros de desconto e frete não contaminam chamadas seguintes.
        with pytest.raises(ValueError):
            calcular_total([(2, 100)], desconto=150, frete=50)
        with pytest.raises(ValueError):
            calcular_total([(2, 100)], desconto=-5, frete=50)
        with pytest.raises(ValueError):
            calcular_total([(2, 100)], desconto=10, frete=-50)
        assert calcular_total([(2, 100)]) == 200
        assert calcular_total([(2, 100)], desconto=10, frete=50) == 230
