import pytest

from carrinho import calcular_total


class TestCalculoBasicoEAssinatura:
    def test_carrinho_vazio_sem_opcionais(self):
        resultado = calcular_total([])
        assert resultado == 0
        assert type(resultado) is int

    @pytest.mark.parametrize(
        "desconto,frete",
        [
            (0, 0),
            (0, 500),
            (25, 0),
            (25, 500),
            (100, 0),
            (100, 500),
        ],
    )
    def test_carrinho_vazio_com_opcionais_validos(self, desconto, frete):
        resultado = calcular_total([], desconto=desconto, frete=frete)
        assert resultado == 0
        assert type(resultado) is int

    def test_item_unico_e_multiplos_itens(self):
        assert calcular_total([(1, 250)]) == 250
        assert calcular_total([(3, 250)]) == 750
        assert calcular_total([(2, 150), (3, 400), (1, 50)]) == 1550

    def test_itens_duplicados_sao_somados_individualmente(self):
        assert calcular_total([(1, 100), (1, 100)]) == 200
        assert calcular_total([(2, 350), (2, 350), (1, 100)]) == 1500

    def test_argumentos_posicionais_nomeados_e_padroes(self):
        itens = [(2, 300), (1, 400)]
        assert calcular_total(itens) == 1000
        assert calcular_total(itens, 10) == 900
        assert calcular_total(itens, 10, 250) == 1150
        assert calcular_total(itens, desconto=10) == 900
        assert calcular_total(itens, frete=250) == 1250
        assert calcular_total(itens=itens, desconto=10, frete=250) == 1150

    def test_tipo_de_retorno_sempre_int(self):
        casos = [
            ([(1, 100)], 0, 0, 100),
            ([(1, 100)], 10, 0, 90),
            ([(1, 100)], 100, 0, 0),
            ([(1, 100)], 100, 500, 500),
            ([(1, 101)], 10, 50, 140),
            ([(0, 100)], 50, 500, 0),
        ]
        for itens, desconto, frete, esperado in casos:
            resultado = calcular_total(itens, desconto=desconto, frete=frete)
            assert resultado == esperado
            assert type(resultado) is int


class TestDescontoETruncamento:
    def test_bordas_desconto_zero_e_cem(self):
        assert calcular_total([(2, 350)], desconto=0) == 700
        assert calcular_total([(2, 350)], desconto=100) == 0
        assert calcular_total([(2, 350)], desconto=0, frete=150) == 850
        assert calcular_total([(2, 350)], desconto=100, frete=150) == 150
        assert calcular_total([(1, 0)], desconto=0, frete=150) == 150
        assert calcular_total([(1, 0)], desconto=100, frete=150) == 150

    @pytest.mark.parametrize(
        "itens,desconto,esperado",
        [
            # Evita subtracao do desconto truncado (bruto - bruto*d//100) e teto
            ([(1, 1)], 1, 0),
            ([(1, 1)], 50, 0),
            ([(1, 101)], 10, 90),  # 90.9 -> 90 (nao 91)
            ([(1, 101)], 99, 1),  # 1.01 -> 1 (nao 2)
            # Evita arredondamento (round / half-up) em metades pares, impares e > 0.5
            ([(1, 199)], 50, 99),  # 99.5 -> 99 (nao 100)
            ([(1, 201)], 50, 100),  # 100.5 -> 100 (nao 101)
            ([(1, 3)], 10, 2),  # 2.7 -> 2 (nao 3)
            ([(1, 199)], 99, 1),  # 1.99 -> 1 (nao 2)
            # Descontos exatos (tambem capturam imprecisao de float binario em 1 - d/100)
            ([(1, 100)], 7, 93),
            ([(1, 100)], 14, 86),
            ([(1, 100)], 29, 71),
            ([(1, 100)], 55, 45),
            ([(1, 100)], 58, 42),
            ([(1, 1000)], 7, 930),
            ([(1, 1000)], 14, 860),
            ([(1, 1000)], 55, 450),
            ([(1, 1000)], 58, 420),
        ],
    )
    def test_truncamento_para_baixo_e_exatidao(self, itens, desconto, esperado):
        resultado = calcular_total(itens, desconto=desconto)
        assert resultado == esperado
        assert type(resultado) is int

    def test_truncamento_agregado_entre_linhas(self):
        # Desconto aplicado uma unica vez sobre o bruto, nunca por linha
        assert calcular_total([(1, 1), (1, 1)], desconto=50) == 1
        assert calcular_total([(1, 33), (1, 33), (1, 34)], desconto=10) == 90
        assert calcular_total([(1, 12), (1, 12), (1, 12)], desconto=10) == 32
        assert calcular_total([(1, 1), (1, 1), (1, 1), (1, 1)], desconto=75) == 1
        assert calcular_total([(0, 999), (1, 12), (0, 500), (2, 12)], desconto=10) == 32

    def test_desconto_nao_e_aplicado_por_unidade_antes_da_quantidade(self):
        # 2 * 1 = 2; 2 * 50 // 100 = 1 (por unidade daria 2 * 0 = 0)
        assert calcular_total([(2, 1)], desconto=50) == 1
        # 3 * 12 = 36; 36 * 90 // 100 = 32 (por unidade daria 3 * 10 = 30)
        assert calcular_total([(3, 12)], desconto=10) == 32
        # 10 * 19 = 190; 190 * 90 // 100 = 171 (por unidade daria 10 * 17 = 170)
        assert calcular_total([(10, 19)], desconto=10) == 171

    def test_desconto_nao_incide_sobre_frete(self):
        assert calcular_total([(1, 1000)], desconto=50, frete=500) == 1000
        assert calcular_total([(1, 1000)], desconto=33, frete=100) == 770
        assert calcular_total([(1, 1000)], desconto=100, frete=500) == 500
        assert calcular_total([(2, 501)], desconto=10, frete=333) == 1234


class TestFreteEQuantidadesZero:
    def test_somente_linhas_com_quantidade_zero_nao_pagam_frete(self):
        assert calcular_total([(0, 0)], frete=500) == 0
        assert calcular_total([(0, 1000)], frete=500) == 0
        assert calcular_total([(0, 0), (0, 500), (0, 9999)], frete=500) == 0
        assert calcular_total([(0, 1000)], desconto=20, frete=500) == 0

    def test_item_gratuito_com_quantidade_positiva_paga_frete(self):
        assert calcular_total([(1, 0)], frete=500) == 500
        assert calcular_total([(5, 0)], frete=500) == 500
        assert calcular_total([(1, 0)], desconto=0, frete=500) == 500
        assert calcular_total([(1, 0)], desconto=50, frete=500) == 500
        assert calcular_total([(1, 0)], desconto=100, frete=500) == 500
        assert calcular_total([(0, 1000), (1, 0)], frete=500) == 500
        assert calcular_total([(1, 0), (0, 1000)], frete=500) == 500

    def test_liquido_zerado_por_desconto_com_quantidade_positiva_paga_frete(self):
        assert calcular_total([(1, 1)], desconto=50, frete=500) == 500
        assert calcular_total([(2, 1000)], desconto=100, frete=350) == 350

    def test_frete_cobrado_uma_unica_vez_com_varias_linhas_e_unidades(self):
        assert calcular_total([(1, 100)], frete=500) == 600
        assert calcular_total([(3, 100), (2, 200)], frete=500) == 1200
        assert calcular_total([(0, 500), (2, 300), (0, 100), (1, 0)], frete=400) == 1000

    def test_linhas_posteriores_a_quantidade_zero_sao_contabilizadas(self):
        assert calcular_total([(0, 500), (2, 300)], frete=100) == 700
        assert calcular_total([(0, 0), (0, 100), (1, 250)], desconto=10, frete=50) == 275


class TestPrecisaoArbitraria:
    def test_exatidao_acima_de_2_elevado_53_sem_desconto(self):
        valor = (1 << 53) + 1
        resultado = calcular_total([(1, valor)], desconto=0, frete=0)
        assert resultado == 9007199254740993
        assert type(resultado) is int

        resultado_com_frete = calcular_total([(1, valor)], desconto=0, frete=2)
        assert resultado_com_frete == 9007199254740995
        assert type(resultado_com_frete) is int

    def test_exatidao_acima_de_2_elevado_53_com_desconto_e_truncamento(self):
        base = (1 << 53) + 1
        # (base * 100) * 99 // 100 == base * 99 exatamente
        assert calcular_total([(1, base * 100)], desconto=1) == base * 99
        # (base * 100 + 99) * 50 // 100 == base * 50 + 49
        assert calcular_total([(1, base * 100 + 99)], desconto=50) == base * 50 + 49
        # Soma de multiplos itens grandes com truncamento e frete grande
        p1 = (1 << 60) + 37
        p2 = (1 << 60) + 19
        frete = (1 << 55) + 7
        bruto_esperado = p1 + 2 * p2
        esperado = bruto_esperado * 83 // 100 + frete
        resultado = calcular_total([(1, p1), (2, p2)], desconto=17, frete=frete)
        assert resultado == esperado
        assert type(resultado) is int

    def test_inteiros_muito_grandes_acima_de_64_bits(self):
        qtd = 10**18 + 3
        preco = 10**6 + 7
        frete = 10**20 + 1
        esperado = (qtd * preco) * 87 // 100 + frete
        resultado = calcular_total([(qtd, preco)], desconto=13, frete=frete)
        assert resultado == esperado
        assert type(resultado) is int

        grande = (1 << 100) + 51
        resultado_100 = calcular_total([(1, grande)], desconto=50, frete=(1 << 100) + 1)
        assert resultado_100 == ((1 << 99) + 25) + ((1 << 100) + 1)
        assert type(resultado_100) is int


class TestValidacaoEExcecoes:
    @pytest.mark.parametrize("desconto", [-1, -50, 101, 200])
    @pytest.mark.parametrize(
        "itens",
        [
            [],
            [(0, 0)],
            [(0, 500)],
            [(1, 0)],
            [(2, 300)],
        ],
    )
    def test_desconto_invalido_lanca_value_error(self, itens, desconto):
        with pytest.raises(ValueError):
            calcular_total(itens, desconto=desconto)

    @pytest.mark.parametrize("frete", [-1, -100, -(1 << 60)])
    @pytest.mark.parametrize(
        "itens,desconto",
        [
            ([], 0),
            ([], 100),
            [(0, 0)],
            [(0, 500)],
            [(1, 0)],
            [(2, 300)],
        ]
        if False
        else [
            ([], 0),
            ([], 100),
            ([(0, 0)], 0),
            ([(0, 500)], 50),
            ([(1, 0)], 0),
            ([(2, 300)], 0),
            ([(2, 300)], 100),
        ],
    )
    def test_frete_negativo_lanca_value_error(self, itens, desconto, frete):
        with pytest.raises(ValueError):
            calcular_total(itens, desconto=desconto, frete=frete)

    @pytest.mark.parametrize(
        "itens,desconto",
        [
            ([(-1, 100)], 0),
            ([(-1, 0)], 0),
            ([(-1, 100)], 100),
            ([(-1, -100)], 0),
            ([(5, 100), (-1, 100)], 0),  # total de unidades e bruto continuam positivos
            ([(1, 100), (-1, 100)], 0),  # soma de unidades e bruto zeram
            ([(0, 100), (-1, 50)], 0),  # apos linha de quantidade zero
            ([(2, 300), (0, 100), (-1, 50)], 10),
            ([(-2, 50), (3, 100)], 0),  # erro na primeira linha
            ([(3, 100), (-2, 50), (1, 100)], 0),  # erro no meio
        ],
    )
    def test_quantidade_negativa_lanca_value_error(self, itens, desconto):
        with pytest.raises(ValueError):
            calcular_total(itens, desconto=desconto)

    @pytest.mark.parametrize(
        "itens,desconto",
        [
            ([(1, -1)], 0),
            ([(1, -100)], 100),
            ([(0, -1)], 0),  # quantidade zero com preco negativo
            ([(0, -100)], 50),
            ([(2, 500), (0, -1)], 0),
            ([(0, -1), (2, 500)], 0),
            ([(2, 500), (1, -100)], 0),  # bruto continua positivo
            ([(0, 100), (1, -1)], 0),  # apos linha de quantidade zero
            ([(2, 300), (0, 100), (1, -50)], 10),
            ([(1, -1), (3, 100)], 0),  # erro na primeira linha
            ([(3, 100), (1, -1), (2, 200)], 0),  # erro no meio
        ],
    )
    def test_preco_negativo_lanca_value_error(self, itens, desconto):
        with pytest.raises(ValueError):
            calcular_total(itens, desconto=desconto)


class TestImutabilidadeEIndependencia:
    def test_lista_nao_e_alterada_em_chamadas_validas(self):
        itens = [(2, 300), (0, 500), (1, 100), (3, 0), (2, 300)]
        copia = list(itens)
        assert calcular_total(itens, desconto=15, frete=250) == 1355
        assert itens == copia

        assert calcular_total(itens, desconto=100, frete=250) == 250
        assert itens == copia

        vazio = []
        assert calcular_total(vazio, desconto=10, frete=500) == 0
        assert vazio == []

    @pytest.mark.parametrize(
        "itens,desconto,frete",
        [
            ([(2, 300), (0, 500), (1, 100)], -1, 0),
            ([(2, 300), (0, 500), (1, 100)], 101, 0),
            ([(2, 300), (0, 500), (1, 100)], 10, -1),
            ([(-1, 300), (0, 500), (1, 100)], 0, 0),
            ([(2, 300), (0, 500), (-1, 100)], 0, 0),
            ([(2, 300), (-1, 500), (1, 100)], 0, 0),
            ([(2, 300), (0, -1), (1, 100)], 0, 0),
            ([(2, 300), (0, 500), (1, -1)], 0, 0),
            ([(0, 500), (1, -10)], 20, 100),
            ([], -1, 0),
            ([], 0, -1),
        ],
    )
    def test_lista_permanece_intacta_apos_value_error(self, itens, desconto, frete):
        copia = list(itens)
        with pytest.raises(ValueError):
            calcular_total(itens, desconto=desconto, frete=frete)
        assert itens == copia

    def test_chamadas_sao_independentes(self):
        itens = [(2, 100), (1, 50)]
        assert calcular_total(itens, desconto=10, frete=50) == 275
        assert calcular_total(itens, desconto=20, frete=50) == 250
        assert calcular_total(itens, desconto=10, frete=80) == 305
        assert calcular_total(itens, desconto=10, frete=50) == 275
        assert calcular_total(itens) == 250
        assert calcular_total([], frete=500) == 0
        assert calcular_total([(0, 100)], frete=500) == 0

    def test_estado_preservado_apos_erros(self):
        assert calcular_total([(2, 300)], desconto=10, frete=100) == 640

        for itens_invalidos, desconto, frete in [
            ([(5, 1000), (-1, 100)], 0, 0),
            ([(5, 1000), (1, -100)], 10, 200),
            ([(5, 1000), (0, -1)], 0, 100),
            ([(5, 1000)], -5, 100),
            ([(5, 1000)], 105, 100),
            ([(5, 1000)], 10, -50),
        ]:
            copia = list(itens_invalidos)
            with pytest.raises(ValueError):
                calcular_total(itens_invalidos, desconto=desconto, frete=frete)
            assert itens_invalidos == copia
            # Apos cada erro, novas chamadas validas continuam exatas e independentes
            assert calcular_total([(2, 300)], desconto=10, frete=100) == 640
            assert calcular_total([], frete=500) == 0
            assert calcular_total([(1, 100)]) == 100
