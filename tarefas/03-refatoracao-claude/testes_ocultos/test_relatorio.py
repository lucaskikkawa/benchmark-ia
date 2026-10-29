import pytest

import relatorio
from relatorio import gerar_relatorio


def pedido(cliente, tipo, itens):
    return {"cliente": cliente, "tipo": tipo, "itens": [{"preco": p, "qtd": q} for p, q in itens]}


# ---- comportamento (strings obtidas da versão original) ----

def test_lista_vazia():
    assert gerar_relatorio([]) == "TOTAL: 0.00"


def test_um_pedido_vip():
    assert gerar_relatorio([pedido("Ana", "vip", [(100.0, 2), (50.5, 1)])]) == "Ana: 225.45\nTOTAL: 225.45"


def test_todas_as_faixas():
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


def test_qtd_zero_nao_e_erro():
    assert gerar_relatorio([pedido("Ana", "comum", [(10.0, 0), (4.0, 1)])]) == "Ana: 4.00\nTOTAL: 4.00"


def test_qtd_negativa_levanta_value_error():
    with pytest.raises(ValueError):
        gerar_relatorio([pedido("Ana", "vip", [(10.0, 1), (5.0, -1)])])


def test_nao_modifica_entrada():
    pedidos = [pedido("Ana", "vip", [(10.0, 1)])]
    copia = [dict(p, itens=[dict(i) for i in p["itens"]]) for p in pedidos]
    gerar_relatorio(pedidos)
    assert pedidos == copia


# ---- estrutura exigida no enunciado ----

def test_calcular_subtotal():
    assert relatorio.calcular_subtotal([{"preco": 2.5, "qtd": 4}, {"preco": 1.0, "qtd": 3}]) == pytest.approx(13.0)
    assert relatorio.calcular_subtotal([]) == 0


def test_calcular_subtotal_qtd_negativa():
    with pytest.raises(ValueError):
        relatorio.calcular_subtotal([{"preco": 1.0, "qtd": -2}])


@pytest.mark.parametrize(
    "subtotal, tipo, desconto",
    [
        (500.0, "vip", 50.0),
        (2000.0, "vip", 300.0),
        (1000.0, "vip", 100.0),
        (400.0, "atacado", 20.0),
        (1500.0, "atacado", 120.0),
        (800.0, "comum", 0.0),
        (1000.0, "desconhecido", 0.0),
        (5000.0, "qualquer", 100.0),
    ],
)
def test_calcular_desconto(subtotal, tipo, desconto):
    assert relatorio.calcular_desconto(subtotal, tipo) == pytest.approx(desconto)


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
