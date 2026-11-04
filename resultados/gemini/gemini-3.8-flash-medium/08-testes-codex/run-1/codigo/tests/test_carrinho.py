import pytest
from carrinho import calcular_total


class TestValidacaoExcecoes:
    """Testes de validação dos argumentos e lançamento de ValueError."""

    def test_desconto_negativo_lanca_value_error(self):
        with pytest.raises(ValueError):
            calcular_total([(1, 100)], desconto=-1)

    def test_desconto_negativo_com_carrinho_vazio(self):
        with pytest.raises(ValueError):
            calcular_total([], desconto=-1)

    def test_desconto_negativo_com_quantidade_zero(self):
        with pytest.raises(ValueError):
            calcular_total([(0, 100)], desconto=-5)

    def test_desconto_maior_que_100_lanca_value_error(self):
        with pytest.raises(ValueError):
            calcular_total([(1, 100)], desconto=101)

    def test_desconto_maior_que_100_com_carrinho_vazio(self):
        with pytest.raises(ValueError):
            calcular_total([], desconto=101)

    def test_desconto_maior_que_100_com_quantidade_zero(self):
        with pytest.raises(ValueError):
            calcular_total([(0, 100)], desconto=150)

    def test_frete_negativo_lanca_value_error(self):
        with pytest.raises(ValueError):
            calcular_total([(1, 100)], frete=-1)

    def test_frete_negativo_com_carrinho_vazio(self):
        with pytest.raises(ValueError):
            calcular_total([], frete=-1)

    def test_frete_negativo_com_quantidade_zero(self):
        with pytest.raises(ValueError):
            calcular_total([(0, 100)], frete=-10)

    def test_quantidade_negativa_lanca_value_error(self):
        with pytest.raises(ValueError):
            calcular_total([(-1, 100)])

    def test_quantidade_negativa_com_preco_zero(self):
        with pytest.raises(ValueError):
            calcular_total([(-1, 0)])

    def test_preco_negativo_lanca_value_error(self):
        with pytest.raises(ValueError):
            calcular_total([(1, -1)])

    def test_preco_negativo_com_quantidade_zero(self):
        with pytest.raises(ValueError):
            calcular_total([(0, -1)])

    def test_validacao_linhas_posteriores_a_quantidade_zero_quantidade_negativa(self):
        with pytest.raises(ValueError):
            calcular_total([(0, 100), (-1, 50)])

    def test_validacao_linhas_posteriores_a_quantidade_zero_preco_negativo(self):
        with pytest.raises(ValueError):
            calcular_total([(0, 100), (2, -10)])

    def test_validacao_multiplas_linhas_zero_seguidas_de_invalida(self):
        with pytest.raises(ValueError):
            calcular_total([(0, 0), (0, 10), (0, -5)])


class TestBordasEValoresValidos:
    """Testes de valores limite permitidos pelo contrato."""

    def test_desconto_zero(self):
        assert calcular_total([(1, 100)], desconto=0) == 100

    def test_desconto_cem(self):
        assert calcular_total([(1, 100)], desconto=100) == 0

    def test_desconto_cem_com_frete(self):
        assert calcular_total([(1, 100)], desconto=100, frete=50) == 50

    def test_frete_zero(self):
        assert calcular_total([(1, 100)], frete=0) == 100

    def test_carrinho_vazio_retorna_zero(self):
        assert calcular_total([]) == 0

    def test_carrinho_vazio_com_frete_retorna_zero(self):
        assert calcular_total([], frete=50) == 0

    def test_carrinho_vazio_com_desconto_e_frete_retorna_zero(self):
        assert calcular_total([], desconto=20, frete=50) == 0

    def test_item_quantidade_zero_sem_frete(self):
        assert calcular_total([(0, 100)], frete=50) == 0

    def test_multiplos_itens_quantidade_zero_sem_frete(self):
        assert calcular_total([(0, 100), (0, 200)], frete=50) == 0

    def test_item_gratuito_com_quantidade_positiva_paga_frete(self):
        assert calcular_total([(1, 0)], frete=50) == 50

    def test_item_gratuito_com_desconto_paga_frete(self):
        assert calcular_total([(3, 0)], desconto=50, frete=40) == 40

    def test_mistura_item_quantidade_zero_e_item_com_unidades(self):
        assert calcular_total([(0, 50), (2, 30)], frete=10) == 70

    def test_quantidade_zero_no_meio_da_lista(self):
        assert calcular_total([(1, 40), (0, 50), (2, 30)], frete=10) == 110

    def test_item_gratuito_com_desconto_cem_paga_frete(self):
        assert calcular_total([(5, 0)], desconto=100, frete=50) == 50

    def test_argumentos_padrao(self):
        assert calcular_total([(2, 50)]) == 100
        assert calcular_total([(2, 50)], desconto=10) == 90
        assert calcular_total([(2, 50)], frete=15) == 115


class TestRegrasCalculoEDesconto:
    """Testes de cálculo do valor bruto, desconto único e frete sem desconto."""

    def test_frete_nao_sofre_desconto(self):
        # Bruto = 100, desconto = 50% -> liquido = 50. Frete = 40. Total = 90.
        # Se o frete sofresse desconto: (100 + 40) * 50 // 100 = 70.
        assert calcular_total([(1, 100)], desconto=50, frete=40) == 90

    def test_truncamento_agregado_entre_linhas(self):
        # Itens: 1x50 e 1x50 -> Bruto = 100. Desconto = 5%.
        # Agregado: 100 * 95 // 100 = 95.
        # Se truncasse por linha: (50 * 95 // 100) + (50 * 95 // 100) = 47 + 47 = 94.
        assert calcular_total([(1, 50), (1, 50)], desconto=5) == 95

        # Itens: 3 itens de valor 1. Desconto = 33%.
        # Agregado: 3 * 67 // 100 = 201 // 100 = 2.
        # Por linha: 1 * 67 // 100 = 0 -> soma = 0.
        assert calcular_total([(1, 1), (1, 1), (1, 1)], desconto=33) == 2

        # Itens: 1x33, 1x33, 1x34 -> Bruto = 100. Desconto = 10%.
        # Agregado: 100 * 90 // 100 = 90.
        # Por linha: 29 + 29 + 30 = 88.
        assert calcular_total([(1, 33), (1, 33), (1, 34)], desconto=10) == 90

    def test_formula_desconto_trunca_para_baixo_exato(self):
        # Testa que a fórmula é bruto * (100 - desconto) // 100
        # e não bruto - (bruto * desconto // 100).
        # Bruto = 10, desconto = 15:
        # bruto * (100 - 15) // 100 = 10 * 85 // 100 = 8.
        # bruto - (bruto * 15 // 100) = 10 - 1 = 9.
        assert calcular_total([(1, 10)], desconto=15) == 8

        # Bruto = 3, desconto = 50:
        # 3 * 50 // 100 = 1.
        # 3 - (3 * 50 // 100) = 3 - 1 = 2.
        assert calcular_total([(1, 3)], desconto=50) == 1

    def test_truncamento_para_baixo_vs_arredondamento(self):
        # Bruto = 15, desconto = 10%:
        # 15 * 90 // 100 = 13.
        # Arredondando 15 * 0.9 = 13.5 daria 14.
        assert calcular_total([(1, 15)], desconto=10) == 13

        # Bruto = 7, desconto = 20%:
        # 7 * 80 // 100 = 5.
        # 7 * 0.8 = 5.6 -> round daria 6.
        assert calcular_total([(1, 7)], desconto=20) == 5

    def test_calculo_geral_multiplos_itens(self):
        itens = [(3, 150), (2, 250), (1, 99)]
        # bruto = 450 + 500 + 99 = 1049
        # unidades = 6
        # desconto = 15% -> 1049 * 85 // 100 = 891
        # frete = 350 -> 891 + 350 = 1241
        assert calcular_total(itens, desconto=15, frete=350) == 1241


class TestPrecisaoArbitraria:
    """Testes com inteiros de precisão arbitrária acima de 2**53."""

    def test_inteiro_acima_de_2_a_53_sem_perda_de_precisao(self):
        # 2**55 + 3 = 36028797018963971
        # Com desconto de 50%:
        # (2**55 + 3) * 50 // 100 = 2**54 + 1 = 18014398509481985
        # Em float de 64 bits, float(2**55 + 3) perde os bits menos significativos:
        # float(2**55 + 3) * 0.5 = 2**54 = 18014398509481984.
        p = (2**55) + 3
        res = calcular_total([(1, p)], desconto=50)
        assert res == (2**54) + 1
        assert type(res) is int

    def test_inteiro_acima_de_2_a_53_com_desconto_zero(self):
        p = (2**54) + 1
        res = calcular_total([(1, p)], desconto=0)
        assert res == (2**54) + 1
        assert type(res) is int

    def test_frete_acima_de_2_a_53(self):
        f = (2**54) + 1
        res = calcular_total([(1, 0)], frete=f)
        assert res == (2**54) + 1
        assert type(res) is int

    def test_inteiros_grandes_com_frete(self):
        q = 10**18
        p = 10**18
        frete = 10**18 + 7
        desconto = 25
        # bruto = 10**36
        # liquido = 10**36 * 75 // 100 = 75 * 10**34
        esperado = (10**36 * 75 // 100) + frete
        res = calcular_total([(q, p)], desconto=desconto, frete=frete)
        assert res == esperado
        assert type(res) is int

    def test_tipo_de_retorno_sempre_int(self):
        res = calcular_total([(1, 100)])
        assert type(res) is int
        assert res is not True and res is not False

        res_zero = calcular_total([])
        assert type(res_zero) is int


class TestImutabilidadeEIndependencia:
    """Testes garantindo que a lista recebida não é modificada e as chamadas são independentes."""

    def test_lista_permanece_intacta_em_sucesso(self):
        itens = [(1, 100), (0, 50), (2, 200)]
        backup = [(1, 100), (0, 50), (2, 200)]
        calcular_total(itens, desconto=10, frete=15)
        assert itens == backup

    def test_lista_permanece_intacta_quando_lanca_value_error_na_linha(self):
        itens = [(1, 100), (-1, 50), (2, 200)]
        backup = [(1, 100), (-1, 50), (2, 200)]
        with pytest.raises(ValueError):
            calcular_total(itens)
        assert itens == backup

    def test_lista_permanece_intacta_quando_lanca_value_error_em_linha_posterior_a_zero(self):
        itens = [(0, 10), (1, 20), (0, -1)]
        backup = [(0, 10), (1, 20), (0, -1)]
        with pytest.raises(ValueError):
            calcular_total(itens)
        assert itens == backup

    def test_lista_permanece_intacta_quando_lanca_value_error_no_desconto(self):
        itens = [(1, 100), (2, 200)]
        backup = [(1, 100), (2, 200)]
        with pytest.raises(ValueError):
            calcular_total(itens, desconto=-1)
        assert itens == backup

    def test_lista_permanece_intacta_quando_lanca_value_error_no_frete(self):
        itens = [(1, 100), (2, 200)]
        backup = [(1, 100), (2, 200)]
        with pytest.raises(ValueError):
            calcular_total(itens, frete=-1)
        assert itens == backup

    def test_chamadas_sao_independentes(self):
        itens = [(2, 50)]
        assert calcular_total(itens, frete=10) == 110
        assert calcular_total([], frete=10) == 0
        assert calcular_total(itens, frete=10) == 110
