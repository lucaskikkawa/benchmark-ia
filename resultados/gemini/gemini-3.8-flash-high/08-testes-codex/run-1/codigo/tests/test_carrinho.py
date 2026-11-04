import sys
from pathlib import Path

# Garante que o diretório raiz do projeto esteja no sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from carrinho import calcular_total


class TestValidacaoParametrosGlobais:
    """Validações dos parâmetros globais: desconto e frete."""

    @pytest.mark.parametrize("desconto_invalido", [-100, -50, -1, 101, 150, 200])
    def test_desconto_fora_da_faixa_lanca_value_error(self, desconto_invalido):
        with pytest.raises(ValueError):
            calcular_total([(1, 100)], desconto=desconto_invalido)

    @pytest.mark.parametrize("frete_invalido", [-100, -50, -1])
    def test_frete_negativo_lanca_value_error(self, frete_invalido):
        with pytest.raises(ValueError):
            calcular_total([(1, 100)], frete=frete_invalido)

    @pytest.mark.parametrize("desconto_invalido", [-10, -1, 101, 105])
    def test_desconto_invalido_com_carrinho_vazio(self, desconto_invalido):
        with pytest.raises(ValueError):
            calcular_total([], desconto=desconto_invalido)

    @pytest.mark.parametrize("frete_invalido", [-10, -1])
    def test_frete_negativo_com_carrinho_vazio(self, frete_invalido):
        with pytest.raises(ValueError):
            calcular_total([], frete=frete_invalido)

    @pytest.mark.parametrize("desconto_invalido", [-1, 101])
    def test_desconto_invalido_com_itens_quantidade_zero(self, desconto_invalido):
        with pytest.raises(ValueError):
            calcular_total([(0, 100)], desconto=desconto_invalido)

    @pytest.mark.parametrize("frete_invalido", [-1, -10])
    def test_frete_negativo_com_itens_quantidade_zero(self, frete_invalido):
        with pytest.raises(ValueError):
            calcular_total([(0, 100)], frete=frete_invalido)

    def test_bordas_validas_desconto_e_frete(self):
        res0 = calcular_total([(1, 100)], desconto=0, frete=0)
        assert res0 == 100
        assert type(res0) is int

        res100 = calcular_total([(1, 100)], desconto=100, frete=0)
        assert res100 == 0
        assert type(res100) is int

        res100_frete = calcular_total([(1, 100)], desconto=100, frete=50)
        assert res100_frete == 50
        assert type(res100_frete) is int


class TestValidacaoItens:
    """Validações de quantidade e preço dos itens."""

    @pytest.mark.parametrize("quantidade_invalida", [-1, -10, -100])
    def test_quantidade_negativa_lanca_value_error(self, quantidade_invalida):
        with pytest.raises(ValueError):
            calcular_total([(quantidade_invalida, 100)])

    @pytest.mark.parametrize("preco_invalido", [-1, -10, -100])
    def test_preco_negativo_lanca_value_error(self, preco_invalido):
        with pytest.raises(ValueError):
            calcular_total([(1, preco_invalido)])

    @pytest.mark.parametrize("preco_invalido", [-1, -50])
    def test_preco_negativo_com_quantidade_zero_lanca_value_error(self, preco_invalido):
        with pytest.raises(ValueError):
            calcular_total([(0, preco_invalido)])

    def test_validacao_linhas_posteriores_a_quantidade_zero(self):
        with pytest.raises(ValueError):
            calcular_total([(0, 100), (-1, 50)])

        with pytest.raises(ValueError):
            calcular_total([(0, 100), (1, -1)])

        with pytest.raises(ValueError):
            calcular_total([(0, 100), (0, -1)])

        with pytest.raises(ValueError):
            calcular_total([(0, 0), (0, 0), (-2, 10)])

        with pytest.raises(ValueError):
            calcular_total([(1, 50), (0, 20), (2, -10)])

    def test_quantidade_zero_e_preco_zero_sao_validos(self):
        assert calcular_total([(0, 0)]) == 0
        assert calcular_total([(0, 100)]) == 0
        assert calcular_total([(1, 0)]) == 0


class TestRegrasFrete:
    """Regras de incidência e cálculo do frete."""

    def test_frete_nao_cobrado_em_carrinho_vazio(self):
        res = calcular_total([], frete=100)
        assert res == 0
        assert type(res) is int

        res2 = calcular_total([], desconto=20, frete=50)
        assert res2 == 0
        assert type(res2) is int

    def test_frete_nao_cobrado_com_apenas_quantidade_zero(self):
        assert calcular_total([(0, 500)], frete=100) == 0
        assert calcular_total([(0, 100), (0, 200)], frete=50) == 0
        assert calcular_total([(0, 0)], frete=75) == 0

    def test_item_gratuito_com_quantidade_positiva_paga_frete(self):
        assert calcular_total([(1, 0)], frete=100) == 100
        assert calcular_total([(3, 0)], frete=250) == 250
        assert calcular_total([(0, 100), (2, 0)], frete=80) == 80
        assert calcular_total([(2, 0)], desconto=50, frete=120) == 120

    def test_frete_adicionado_sem_desconto(self):
        # Desconto de 50% em bruto de 100 dá 50. Frete de 40 sem desconto = 90.
        assert calcular_total([(1, 100)], desconto=50, frete=40) == 90
        # Desconto de 100% zera o bruto. Frete de 300 permanece 300.
        assert calcular_total([(1, 1000)], desconto=100, frete=300) == 300
        # Frete não sofre desconto mesmo com múltiplos itens
        assert calcular_total([(2, 500)], desconto=20, frete=150) == 950


class TestRegrasDescontoETruncamento:
    """Regras de cálculo de desconto e truncamento agregado."""

    def test_truncamento_para_baixo_no_desconto(self):
        # 99 * 50 // 100 = 49 (arredondamento comum daria 50)
        assert calcular_total([(1, 99)], desconto=50) == 49
        # 99 * 90 // 100 = 89
        assert calcular_total([(1, 99)], desconto=10) == 89
        # 103 * 50 // 100 = 51 (arredondamento comum daria 52)
        assert calcular_total([(1, 103)], desconto=50) == 51
        # 7 * 85 // 100 = 5
        assert calcular_total([(1, 7)], desconto=15) == 5

    def test_formula_exata_truncamento_desconto(self):
        # bruto * (100 - desconto) // 100
        # Se alguém fizer: bruto - (bruto * desconto // 100),
        # para bruto = 10 e desconto = 15:
        # bruto * (100 - desconto) // 100 = 10 * 85 // 100 = 8.
        # bruto - (bruto * desconto // 100) = 10 - 1 = 9 != 8!
        assert calcular_total([(1, 10)], desconto=15) == 8

    def test_truncamento_agregado_entre_linhas(self):
        # Duas linhas de (1, 15), desconto de 10%:
        # Bruto total = 30 -> 30 * 90 // 100 = 27
        # Se fosse por linha: 15 * 90 // 100 = 13 -> 13 + 13 = 26 != 27
        assert calcular_total([(1, 15), (1, 15)], desconto=10) == 27

        # Três linhas de (1, 7), desconto de 15%:
        # Bruto total = 21 -> 21 * 85 // 100 = 17
        # Se fosse por linha: (7 * 85 // 100) * 3 = 5 * 3 = 15 != 17
        assert calcular_total([(1, 7), (1, 7), (1, 7)], desconto=15) == 17

        # Quatro linhas de (1, 25), desconto de 33%:
        # Bruto total = 100 -> 100 * 67 // 100 = 67
        # Se fosse por linha: (25 * 67 // 100) * 4 = 16 * 4 = 64 != 67
        assert calcular_total([(1, 25)] * 4, desconto=33) == 67

        # Truncamento agregado com frete
        assert calcular_total([(1, 15), (1, 15)], desconto=10, frete=50) == 77

    def test_valores_padrao_desconto_e_frete(self):
        assert calcular_total([(1, 100)]) == 100
        assert calcular_total([(2, 250)]) == 500
        assert calcular_total([(1, 100)], 0) == 100
        assert calcular_total([(1, 100)], 0, 0) == 100


class TestPrecisaoArbitraria:
    """Suporte a inteiros de precisão arbitrária acima de 2**53."""

    def test_inteiros_maiores_que_2_elevado_a_53_sem_perda_de_precisao(self):
        # 2**55 + 1 não pode ser representado com precisão exata em float64 (IEEE 754)
        val = (1 << 55) + 1
        assert float(val) == float(val - 1)  # demonstra a limitação do float

        res = calcular_total([(1, val)])
        assert type(res) is int
        assert res == val
        assert res != val - 1

    def test_calculo_grande_com_desconto_e_frete(self):
        preco = (1 << 62) + 7
        quantidade = 3
        bruto = quantidade * preco
        desconto = 35
        frete = (1 << 60) + 13

        esperado_liquido = bruto * (100 - desconto) // 100
        esperado_total = esperado_liquido + frete

        resultado = calcular_total([(quantidade, preco)], desconto=desconto, frete=frete)
        assert type(resultado) is int
        assert resultado == esperado_total


class TestImutabilidadeDaLista:
    """A lista recebida não deve ser alterada, inclusive em caso de erro."""

    def test_lista_permanece_intacta_apos_sucesso(self):
        itens = [(3, 100), (1, 50), (2, 200), (0, 70)]
        itens_original = list(itens)
        calcular_total(itens, desconto=10, frete=50)
        assert itens == itens_original

    def test_lista_permanece_intacta_apos_value_error_na_validacao_de_item(self):
        itens = [(3, 100), (1, 50), (-1, 200)]
        itens_original = list(itens)
        with pytest.raises(ValueError):
            calcular_total(itens)
        assert itens == itens_original

    def test_lista_permanece_intacta_apos_value_error_de_preco_negativo(self):
        itens = [(3, 100), (0, 50), (2, -40), (1, 10)]
        itens_original = list(itens)
        with pytest.raises(ValueError):
            calcular_total(itens)
        assert itens == itens_original

    def test_lista_permanece_intacta_apos_value_error_de_preco_negativo_com_quantidade_zero(self):
        itens = [(3, 100), (0, -50), (1, 20)]
        itens_original = list(itens)
        with pytest.raises(ValueError):
            calcular_total(itens)
        assert itens == itens_original

    def test_lista_permanece_intacta_apos_value_error_nos_parametros_globais(self):
        itens = [(3, 100), (1, 50), (2, 200)]
        itens_original = list(itens)
        with pytest.raises(ValueError):
            calcular_total(itens, desconto=-5)
        assert itens == itens_original

        with pytest.raises(ValueError):
            calcular_total(itens, frete=-10)
        assert itens == itens_original

    def test_lista_permanece_intacta_apos_erro_posterior_a_quantidade_zero(self):
        itens = [(0, 100), (2, 50), (1, -1)]
        itens_original = list(itens)
        with pytest.raises(ValueError):
            calcular_total(itens)
        assert itens == itens_original


class TestIndependenciaEComposicao:
    """Chamadas sucessivas são independentes e suportam carrinhos compostos."""

    def test_chamadas_sucessivas_sao_independentes(self):
        itens_grandes = [(10, 500)]
        assert calcular_total(itens_grandes, frete=100) == 5100
        assert calcular_total([], frete=100) == 0
        assert calcular_total(itens_grandes, frete=100) == 5100
        assert calcular_total([(1, 50)]) == 50

    def test_carrinho_composto_com_multiplos_tipos_de_linhas(self):
        itens = [
            (0, 500),
            (2, 150),
            (1, 0),
            (0, 0),
            (3, 100),
        ]
        # Unidades = 0 + 2 + 1 + 0 + 3 = 6 > 0
        # Bruto = 0 + 300 + 0 + 0 + 300 = 600
        # Desconto = 15% -> 600 * 85 // 100 = 510
        # Frete = 75
        # Total = 510 + 75 = 585
        resultado = calcular_total(itens, desconto=15, frete=75)
        assert resultado == 585
        assert type(resultado) is int

    def test_linhas_posteriores_a_quantidade_zero_sao_computadas(self):
        itens = [(0, 100), (2, 50), (0, 20), (3, 30)]
        # Unidades = 0 + 2 + 0 + 3 = 5
        # Bruto = 0 + 100 + 0 + 90 = 190
        # Frete = 10
        # Total = 190 + 10 = 200
        assert calcular_total(itens, frete=10) == 200
