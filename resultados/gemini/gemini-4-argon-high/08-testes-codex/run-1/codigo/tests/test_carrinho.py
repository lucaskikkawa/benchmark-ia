import pytest
from carrinho import calcular_total


class TestCalculoBasicoEBordas:
    def test_carrinho_vazio_padrao(self):
        itens = []
        assert calcular_total(itens) == 0
        assert itens == []

    def test_carrinho_vazio_com_frete_e_desconto_nao_cobra_frete(self):
        itens = []
        assert calcular_total(itens, desconto=0, frete=500) == 0
        assert calcular_total(itens, desconto=50, frete=500) == 0
        assert calcular_total(itens, desconto=100, frete=500) == 0
        assert itens == []

    def test_argumentos_default_e_nomeados(self):
        assert calcular_total([(2, 150)]) == 300
        assert calcular_total([(2, 150)], 10) == 270
        assert calcular_total([(2, 150)], 10, 50) == 320
        assert calcular_total(itens=[(2, 150)], frete=50) == 350
        assert calcular_total(itens=[(2, 150)], desconto=10, frete=50) == 320

    def test_multiplos_itens_soma_bruto(self):
        itens = [(1, 100), (2, 250), (3, 50)]
        copia = list(itens)
        resultado = calcular_total(itens)
        assert resultado == 100 + 500 + 150
        assert isinstance(resultado, int)
        assert itens == copia

    def test_desconto_limites_0_e_100(self):
        itens = [(2, 300)]
        assert calcular_total(itens, desconto=0, frete=100) == 700
        assert calcular_total(itens, desconto=100, frete=0) == 0
        assert calcular_total(itens, desconto=100, frete=100) == 100


class TestRegrasDeFreteEQuantidadeZero:
    def test_item_gratuito_com_quantidade_positiva_paga_frete(self):
        assert calcular_total([(1, 0)], desconto=0, frete=450) == 450
        assert calcular_total([(3, 0)], desconto=50, frete=450) == 450
        assert calcular_total([(0, 100), (1, 0)], desconto=0, frete=450) == 450
        assert calcular_total([(1, 0), (0, 100)], desconto=0, frete=450) == 450

    def test_linhas_com_quantidade_zero_nao_pagam_frete(self):
        assert calcular_total([(0, 0)], desconto=0, frete=500) == 0
        assert calcular_total([(0, 100)], desconto=0, frete=500) == 0
        assert calcular_total([(0, 100), (0, 250)], desconto=20, frete=500) == 0

    def test_linha_quantidade_zero_nao_zera_acumulado_anterior_nem_posterior(self):
        assert calcular_total([(2, 100), (0, 500)], desconto=0, frete=300) == 500
        assert calcular_total([(0, 500), (2, 100)], desconto=0, frete=300) == 500
        assert calcular_total([(1, 100), (0, 500), (2, 200)], desconto=10, frete=50) == 500

    def test_frete_nao_sofre_desconto_e_nao_multiplica_por_unidades(self):
        assert calcular_total([(3, 100)], desconto=50, frete=200) == 150 + 200
        assert calcular_total([(1, 1)], desconto=50, frete=200) == 200


class TestTruncamentoEPrecisao:
    def test_truncamento_para_baixo_no_desconto(self):
        # 101 * 99 // 100 = 9999 // 100 = 99 (nao 100 por arredondamento ou bruto - desc_truncado)
        assert calcular_total([(1, 101)], desconto=1) == 99
        # 3 * 50 // 100 = 1 (nao 2)
        assert calcular_total([(1, 3)], desconto=50) == 1
        # 10 * 95 // 100 = 9 (nao 10)
        assert calcular_total([(1, 10)], desconto=5) == 9
        # 199 * 99 // 100 = 197
        assert calcular_total([(1, 199)], desconto=1) == 197
        # 100 * 93 // 100 = 93 (float 100 * (1 - 0.07) daria 92.99999999999999 -> 92)
        assert calcular_total([(1, 100)], desconto=7) == 93

    def test_truncamento_agregado_entre_linhas(self):
        # Cada linha isolada: 15 * 90 // 100 = 13 (soma 26). Agregado: 30 * 90 // 100 = 27.
        assert calcular_total([(1, 15), (1, 15)], desconto=10) == 27
        # 3 linhas de 1 centavo com 50% de desconto: agregado = 3 * 50 // 100 = 1 (por linha seria 0)
        assert calcular_total([(1, 1), (1, 1), (1, 1)], desconto=50) == 1
        # 3 linhas com centavos quebrados
        assert calcular_total([(1, 34), (1, 34), (1, 34)], desconto=10, frete=10) == 91 + 10

    def test_precisao_arbitraria_acima_de_2_53(self):
        grande = (1 << 53) + 1
        assert calcular_total([(1, grande)], desconto=0, frete=0) == grande
        assert calcular_total([(1, grande)], desconto=0, frete=7) == grande + 7

        muito_grande = (1 << 60) + 1234567890123456789
        esperado = (muito_grande * 3 * 87) // 100 + 999
        assert calcular_total([(2, muito_grande), (1, muito_grande)], desconto=13, frete=999) == esperado

        preco_100 = 10**22 + 99
        assert calcular_total([(1, preco_100)], desconto=1, frete=0) == (preco_100 * 99) // 100


class TestValidacoesEExcecoes:
    @pytest.mark.parametrize("desconto_invalido", [-1, -2, -100, 101, 102, 200])
    def test_desconto_invalido_lanca_value_error(self, desconto_invalido):
        with pytest.raises(ValueError):
            calcular_total([(1, 100)], desconto=desconto_invalido)
        with pytest.raises(ValueError):
            calcular_total([], desconto=desconto_invalido)
        with pytest.raises(ValueError):
            calcular_total([(0, 100)], desconto=desconto_invalido)

    @pytest.mark.parametrize("frete_invalido", [-1, -2, -500])
    def test_frete_invalido_lanca_value_error_mesmo_sem_unidades(self, frete_invalido):
        with pytest.raises(ValueError):
            calcular_total([(1, 100)], frete=frete_invalido)
        with pytest.raises(ValueError):
            calcular_total([], frete=frete_invalido)
        with pytest.raises(ValueError):
            calcular_total([(0, 100)], frete=frete_invalido)

    def test_quantidade_negativa_lanca_value_error(self):
        with pytest.raises(ValueError):
            calcular_total([(-1, 100)])
        with pytest.raises(ValueError):
            calcular_total([(-1, 0)])
        with pytest.raises(ValueError):
            calcular_total([(5, 100), (-1, 10)])
        with pytest.raises(ValueError):
            calcular_total([(0, 100), (-1, 100)])
        with pytest.raises(ValueError):
            calcular_total([(-1, -1)])

    def test_preco_negativo_lanca_value_error_inclusive_com_quantidade_zero(self):
        with pytest.raises(ValueError):
            calcular_total([(1, -1)])
        with pytest.raises(ValueError):
            calcular_total([(0, -1)])
        with pytest.raises(ValueError):
            calcular_total([(5, 100), (1, -1)])
        with pytest.raises(ValueError):
            calcular_total([(5, 100), (0, -1)])
        with pytest.raises(ValueError):
            calcular_total([(0, 100), (1, -1)])
        with pytest.raises(ValueError):
            calcular_total([(0, 0), (0, -1)])


class TestImutabilidadeEIndependencia:
    def test_lista_nao_alterada_em_sucesso(self):
        itens = [(2, 100), (0, 50), (3, 200)]
        copia = list(itens)
        assert calcular_total(itens, desconto=15, frete=80) == (800 * 85) // 100 + 80
        assert itens == copia

    def test_lista_intacta_quando_lanca_value_error(self):
        casos = [
            ([(2, 100), (1, 50)], -1, 0),
            ([(2, 100), (1, 50)], 101, 0),
            ([(2, 100), (1, 50)], 0, -1),
            ([(-1, 100), (1, 50)], 0, 0),
            ([(2, 100), (-1, 50)], 0, 0),
            ([(2, 100), (1, -50)], 0, 0),
            ([(0, 100), (0, -1)], 0, 0),
        ]
        for itens, desconto, frete in casos:
            copia = list(itens)
            with pytest.raises(ValueError):
                calcular_total(itens, desconto=desconto, frete=frete)
            assert itens == copia

    def test_preservacao_e_independencia_entre_chamadas_inclusive_apos_erro(self):
        assert calcular_total([(2, 100)], desconto=10, frete=50) == 230

        itens_erro = [(10, 1000), (5, 500), (-1, 10)]
        copia_erro = list(itens_erro)
        with pytest.raises(ValueError):
            calcular_total(itens_erro, desconto=0, frete=300)
        assert itens_erro == copia_erro

        # Chamada subsequente nao pode herdar bruto ou unidades acumulados antes do erro
        assert calcular_total([], desconto=0, frete=300) == 0
        assert calcular_total([(0, 500)], desconto=0, frete=300) == 0
        assert calcular_total([(1, 100)], desconto=0, frete=300) == 400
