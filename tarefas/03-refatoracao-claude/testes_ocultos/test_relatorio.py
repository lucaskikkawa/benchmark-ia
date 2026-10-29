import random

import pytest

import relatorio
from relatorio import gerar_relatorio


def _original(pedidos):
    """Cópia literal da versão original (oráculo de comportamento)."""
    r = {}
    for p in pedidos:
        c = p['cliente']
        t = 0
        for i in p['itens']:
            if i['qtd'] < 0:
                raise ValueError('qtd negativa')
            t = t + i['preco'] * i['qtd']
        if p['tipo'] == 'vip':
            if t > 1000:
                t = t - t * 0.15
            else:
                t = t - t * 0.10
        elif p['tipo'] == 'atacado':
            if t > 1000:
                t = t - t * 0.08
            else:
                t = t - t * 0.05
        else:
            if t > 1000:
                t = t - t * 0.02
            else:
                t = t - t * 0
        if c in r:
            r[c] = r[c] + t
        else:
            r[c] = t
    s = ''
    tot = 0
    for c in sorted(r.keys()):
        s = s + c + ': ' + ('%.2f' % r[c]) + '\n'
        tot = tot + r[c]
    s = s + 'TOTAL: ' + ('%.2f' % tot)
    return s


def resultado(funcao, pedidos):
    try:
        return ("ok", funcao(pedidos))
    except Exception as erro:  # compara só o tipo da exceção
        return ("erro", type(erro))


def assert_igual_ao_original(pedidos):
    assert resultado(gerar_relatorio, pedidos) == resultado(_original, pedidos)


def pedido(cliente, tipo, itens):
    return {"cliente": cliente, "tipo": tipo, "itens": [{"preco": p, "qtd": q} for p, q in itens]}


# ---- comportamento (strings obtidas da versão original) ----

def test_exemplos_basicos():
    assert gerar_relatorio([]) == "TOTAL: 0.00"
    assert gerar_relatorio([pedido("Ana", "vip", [(100.0, 2), (50.5, 1)])]) == "Ana: 225.45\nTOTAL: 225.45"
    pedidos = [
        pedido("Ana", "vip", [(600.0, 2)]),
        pedido("Bruno", "atacado", [(300.0, 1)]),
        pedido("Caio", "atacado", [(250.0, 5)]),
        pedido("Duda", "comum", [(999.9, 1)]),
        pedido("Eva", "comum", [(1200.0, 1)]),
    ]
    esperado = "Ana: 1020.00\nBruno: 285.00\nCaio: 1150.00\nDuda: 999.90\nEva: 1176.00\nTOTAL: 4630.90"
    assert gerar_relatorio(pedidos) == esperado


def test_exatamente_1000_usa_faixa_baixa():
    pedidos = [
        pedido("Ana", "vip", [(1000.0, 1)]),
        pedido("Bia", "atacado", [(500.0, 2)]),
        pedido("Cid", "outro", [(1000.0, 1)]),
    ]
    assert gerar_relatorio(pedidos) == "Ana: 900.00\nBia: 950.00\nCid: 1000.00\nTOTAL: 2850.00"


def test_agrupa_por_cliente_e_ordena():
    pedidos = [
        pedido("Zeca", "vip", [(10.0, 3)]),
        pedido("Ana", "atacado", [(20.0, 1)]),
        pedido("Zeca", "comum", [(5.25, 4)]),
        pedido("Ana", "atacado", []),
    ]
    assert gerar_relatorio(pedidos) == "Ana: 19.00\nZeca: 48.00\nTOTAL: 67.00"


def test_qtd_zero_e_qtd_negativa():
    assert gerar_relatorio([pedido("Ana", "comum", [(10.0, 0), (4.0, 1)])]) == "Ana: 4.00\nTOTAL: 4.00"
    with pytest.raises(ValueError):
        gerar_relatorio([pedido("Ana", "vip", [(10.0, 1), (5.0, -1)])])


def test_nao_modifica_entrada():
    pedidos = [pedido("Ana", "vip", [(10.0, 1)]), pedido("Ana", "comum", [(3.0, 2)])]
    copia = [dict(p, itens=[dict(i) for i in p["itens"]]) for p in pedidos]
    gerar_relatorio(pedidos)
    assert pedidos == copia


# ---- equivalência com o original em entradas difíceis ----

@pytest.mark.parametrize(
    "preco, tipo",
    [
        (1275.1, "vip"),       # 15%
        (858.5, "atacado"),    # 5%
        (2217.875, "atacado"),  # 8%
        (1323.75, "comum"),    # 2%
        (2718.25, "outro"),    # 2%
    ],
)
def test_arredondamento_do_desconto_igual_ao_original(preco, tipo):
    # Nestes valores t - t*taxa e t*(1 - taxa) diferem na 2ª casa decimal.
    assert_igual_ao_original([pedido("Ana", tipo, [(preco, 1)])])


def test_total_somado_na_ordem_alfabetica():
    # Somar os totais na ordem de inserção (ou com sum()/fsum) muda o TOTAL.
    pedidos = [
        pedido("c", "comum", [(1e16, 1)]),
        pedido("b", "comum", [(1.0, 3)]),
        pedido("a", "comum", [(-9.8e15, 1)]),
        pedido("d", "comum", [(-1.0, 1)]),
    ]
    assert_igual_ao_original(pedidos)


def test_acumulo_por_cliente_na_ordem_dos_pedidos():
    pedidos = [
        pedido("Ana", "comum", [(0.1, 1)]),
        pedido("Ana", "comum", [(0.2, 1)]),
        pedido("Ana", "comum", [(0.3, 1)]),
        pedido("Bia", "comum", [(1e17, 1)]),
        pedido("Bia", "comum", [(1.0, 7)]),
        pedido("Bia", "comum", [(-9.8e16, 1)]),
    ]
    assert_igual_ao_original(pedidos)


def test_inf_e_nan():
    assert_igual_ao_original([pedido("Ana", "vip", [(float("inf"), 1)])])
    assert_igual_ao_original([pedido("Ana", "comum", [(float("inf"), 1)]), pedido("Bia", "atacado", [(1.0, 1)])])
    assert_igual_ao_original([pedido("Ana", "atacado", [(float("nan"), 2)])])


def test_precos_inteiros_e_negativos():
    assert_igual_ao_original([pedido("Ana", "comum", [(7, 3)]), pedido("Bia", "vip", [(-50, 2)])])
    assert_igual_ao_original([pedido("Ana", "atacado", [(-2000.5, 1), (10, 1)])])


def test_tipo_comparado_exatamente():
    pedidos = [
        pedido("A", "VIP", [(100.0, 1)]),
        pedido("B", " vip", [(100.0, 1)]),
        pedido("C", "Atacado", [(2000.0, 1)]),
        pedido("D", "vip ", [(2000.0, 1)]),
    ]
    assert gerar_relatorio(pedidos) == _original(pedidos)


def test_nomes_unicode_ordenados_como_str():
    pedidos = [
        pedido("Zé", "comum", [(1.0, 1)]),
        pedido("Álvaro", "comum", [(2.0, 1)]),
        pedido("ana", "comum", [(3.0, 1)]),
        pedido("Ana", "comum", [(4.0, 1)]),
        pedido("Ana ", "comum", [(5.0, 1)]),
    ]
    assert gerar_relatorio(pedidos) == _original(pedidos)


def test_aleatorio_igual_ao_original():
    rng = random.Random(2025)
    tipos = ["vip", "atacado", "comum", "outro", "VIP"]
    clientes = ["Ana", "Bia", "Caio", "Davi", "ana", "Éder"]
    for _ in range(400):
        pedidos = []
        for _ in range(rng.randint(0, 6)):
            itens = []
            for _ in range(rng.randint(0, 4)):
                preco = rng.choice([
                    round(rng.uniform(0, 1500), rng.choice([1, 2, 3])),
                    rng.randint(0, 900),
                    rng.choice([0.1, 0.2, 0.3, 0.005, 0.015, 1000.0, 1000.01]),
                ])
                itens.append((preco, rng.randint(0, 5)))
            pedidos.append(pedido(rng.choice(clientes), rng.choice(tipos), itens))
        assert_igual_ao_original(pedidos)


# ---- exceções em entradas malformadas: mesmo tipo que o original ----

@pytest.mark.parametrize(
    "pedidos",
    [
        [{"tipo": "vip", "itens": [{"preco": 1.0, "qtd": -1}]}],                 # sem cliente + qtd negativa
        [{"cliente": "A", "itens": [{"preco": 1.0, "qtd": -1}]}],                # sem tipo + qtd negativa
        [{"cliente": "A", "tipo": "vip", "itens": [{"qtd": 1}, {"preco": 1.0, "qtd": -1}]}],  # sem preco antes
        [{"cliente": "A", "tipo": "vip", "itens": [{"qtd": -1}]}],               # qtd negativa sem preco
        [{"cliente": "A", "tipo": "vip", "itens": [{"preco": 1.0}]}],            # sem qtd
        [{"cliente": "A", "tipo": "vip"}],                                       # sem itens
        [{"cliente": "A", "tipo": "vip", "itens": []}, {"cliente": "B", "itens": []}],
    ],
    ids=["sem_cliente", "sem_tipo", "sem_preco_antes", "negativa_sem_preco", "sem_qtd", "sem_itens", "segundo_sem_tipo"],
)
def test_excecoes_iguais_ao_original(pedidos):
    esperado = resultado(_original, pedidos)
    assert esperado[0] == "erro"
    assert resultado(gerar_relatorio, pedidos) == esperado


# ---- estrutura exigida no enunciado ----

def test_calcular_subtotal():
    assert relatorio.calcular_subtotal([{"preco": 2.5, "qtd": 4}, {"preco": 1.0, "qtd": 3}]) == pytest.approx(13.0)
    assert relatorio.calcular_subtotal([]) == 0
    with pytest.raises(ValueError):
        relatorio.calcular_subtotal([{"preco": 1.0, "qtd": -2}])


def test_calcular_desconto():
    casos = [
        (500.0, "vip", 50.0),
        (2000.0, "vip", 300.0),
        (1000.0, "vip", 100.0),
        (400.0, "atacado", 20.0),
        (1500.0, "atacado", 120.0),
        (800.0, "comum", 0.0),
        (1000.0, "desconhecido", 0.0),
        (5000.0, "qualquer", 100.0),
        (5000.0, "Vip", 100.0),
    ]
    for subtotal, tipo, desconto in casos:
        assert relatorio.calcular_desconto(subtotal, tipo) == pytest.approx(desconto), (subtotal, tipo)


def test_constantes_de_taxas():
    assert relatorio.LIMITE_FAIXA_ALTA == 1000
    taxas = {tipo: tuple(par) for tipo, par in relatorio.TAXAS_DESCONTO.items()}
    assert taxas == {"vip": (0.10, 0.15), "atacado": (0.05, 0.08)}
    assert tuple(relatorio.TAXAS_PADRAO) == (0, 0.02)


def test_calcular_desconto_consulta_constantes(monkeypatch):
    monkeypatch.setitem(relatorio.TAXAS_DESCONTO, "ouro", (0.25, 0.5))
    assert relatorio.calcular_desconto(100.0, "ouro") == pytest.approx(25.0)
    monkeypatch.setattr(relatorio, "TAXAS_PADRAO", (0.5, 0.5))
    assert relatorio.calcular_desconto(100.0, "comum") == pytest.approx(50.0)
    monkeypatch.setattr(relatorio, "LIMITE_FAIXA_ALTA", 50)
    assert relatorio.calcular_desconto(100.0, "ouro") == pytest.approx(50.0)
    assert gerar_relatorio([pedido("Ana", "ouro", [(100.0, 1)])]) == "Ana: 50.00\nTOTAL: 50.00"


def test_formatar_relatorio():
    # A ordenação alfabética é exigida na saída de gerar_relatorio; formatar pode
    # preservar a ordem recebida ou ordenar ela mesma.
    assert relatorio.formatar_relatorio({"Ana": 2.345, "Bia": 10.0}) == "Ana: 2.35\nBia: 10.00\nTOTAL: 12.35"
    assert relatorio.formatar_relatorio({}) == "TOTAL: 0.00"


def test_gerar_relatorio_usa_calcular_subtotal(monkeypatch):
    monkeypatch.setattr(relatorio, "calcular_subtotal", lambda itens: 80.0)
    assert gerar_relatorio([pedido("Ana", "comum", [(999.0, 1)])]) == "Ana: 80.00\nTOTAL: 80.00"


def test_gerar_relatorio_usa_calcular_desconto(monkeypatch):
    monkeypatch.setattr(relatorio, "calcular_desconto", lambda subtotal, tipo: 0.0)
    assert gerar_relatorio([pedido("Ana", "vip", [(100.0, 1)])]) == "Ana: 100.00\nTOTAL: 100.00"


def test_gerar_relatorio_usa_formatar_relatorio(monkeypatch):
    capturado = {}

    def falso(totais):
        capturado.update(totais)
        return "X"

    monkeypatch.setattr(relatorio, "formatar_relatorio", falso)
    assert gerar_relatorio([pedido("Ana", "atacado", [(100.0, 1)])]) == "X"
    assert capturado == {"Ana": pytest.approx(95.0)}
