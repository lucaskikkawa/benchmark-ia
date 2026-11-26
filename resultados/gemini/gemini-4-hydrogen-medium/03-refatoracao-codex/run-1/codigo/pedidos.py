from collections.abc import Iterable, Mapping
from typing import Any


def subtotal(
    quantidade: int,
    preco_centavos: int,
    desconto_percentual: int = 0,
) -> int:
    """Calcula o subtotal em centavos de um pedido com truncamento por linha."""
    return quantidade * preco_centavos * (100 - desconto_percentual) // 100


def resumo_pedidos(pedidos: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """Agrega quantidade de itens, total em centavos e totais por categoria."""
    total_itens = 0
    total_centavos = 0
    por_categoria: dict[str, int] = {}

    for pedido in pedidos:
        quantidade = pedido['quantidade']
        valor_subtotal = subtotal(
            quantidade,
            pedido['preco_centavos'],
            pedido.get('desconto_percentual', 0),
        )
        total_itens += quantidade
        total_centavos += valor_subtotal
        categoria = pedido['categoria']
        por_categoria[categoria] = por_categoria.get(categoria, 0) + valor_subtotal

    return {
        'itens': total_itens,
        'total_centavos': total_centavos,
        'por_categoria': por_categoria,
    }
