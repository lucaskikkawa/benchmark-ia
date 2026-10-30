"""Processamento de pedidos: cálculo de subtotal, peso, desconto e frete."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ItemPedido:
    nome: str
    preco: float
    quantidade: int = 1
    peso_kg: float = 0.5

    def __post_init__(self) -> None:
        if self.preco < 0.0:
            raise ValueError("preco não pode ser negativo")
        if self.quantidade < 1:
            raise ValueError("quantidade deve ser maior ou igual a 1")
        if self.peso_kg < 0.0:
            raise ValueError("peso_kg não pode ser negativo")

    @property
    def subtotal(self) -> float:
        return round(self.preco * self.quantidade, 2)

    @property
    def peso_total(self) -> float:
        return round(self.peso_kg * self.quantidade, 3)


class CalculadoraFrete:
    """Calcula o frete conforme o tipo e o valor total do pedido."""

    FRETE_GRATIS_A_PARTIR_DE = 200.0

    @staticmethod
    def calcular(tipo: str, peso_kg: float, valor_total: float) -> float:
        if valor_total < 0 or peso_kg < 0:
            raise ValueError("valor_total e peso_kg não podem ser negativos")
        if valor_total >= CalculadoraFrete.FRETE_GRATIS_A_PARTIR_DE:
            return 0.0

        tipo_normalizado = str(tipo).lower()
        if tipo_normalizado == "padrao":
            return round(10.0 + peso_kg * 1.5, 2)
        if tipo_normalizado == "expresso":
            return round(25.0 + peso_kg * 3.0, 2)
        if tipo_normalizado == "economico":
            return round(5.0 + peso_kg * 0.8, 2)
        raise ValueError(f"Tipo de frete desconhecido: {tipo}")


class CalculadoraDesconto:
    """Calcula o desconto conforme a categoria do cliente e o valor total."""

    @staticmethod
    def calcular(categoria_cliente: str, valor_total: float) -> float:
        if valor_total < 0:
            raise ValueError("valor_total não pode ser negativo")

        categoria = str(categoria_cliente).lower()
        if categoria == "prata":
            return round(0.05 * valor_total, 2) if valor_total >= 100.0 else 0.0
        if categoria == "ouro":
            if valor_total >= 50.0:
                return round(0.10 * valor_total, 2)
            return round(0.05 * valor_total, 2)
        if categoria == "vip":
            return round(0.15 * valor_total, 2)
        # "bronze" e demais categorias não recebem desconto
        return 0.0


@dataclass
class Pedido:
    id: str
    cliente: str
    categoria_cliente: str = "bronze"
    itens: list[ItemPedido] = field(default_factory=list)
    tipo_frete: str = "padrao"

    def calcular_total_itens(self) -> float:
        return round(sum((item.subtotal for item in self.itens), 0.0), 2)

    def calcular_peso_total(self) -> float:
        return round(sum((item.peso_total for item in self.itens), 0.0), 3)

    def calcular_desconto(self) -> float:
        return CalculadoraDesconto.calcular(self.categoria_cliente, self.calcular_total_itens())

    def calcular_frete(self) -> float:
        return CalculadoraFrete.calcular(
            self.tipo_frete, self.calcular_peso_total(), self.calcular_total_itens()
        )

    def calcular_total_final(self) -> float:
        return round(
            self.calcular_total_itens() - self.calcular_desconto() + self.calcular_frete(), 2
        )

    def para_dict(self) -> dict:
        return {
            "id": self.id,
            "cliente": self.cliente,
            "subtotal": self.calcular_total_itens(),
            "desconto": self.calcular_desconto(),
            "frete": self.calcular_frete(),
            "total": self.calcular_total_final(),
        }


def _pedido_de_dict(dados: dict) -> Pedido:
    itens = [
        ItemPedido(
            nome=it.get("nome", ""),
            preco=float(it["preco"]),
            quantidade=int(it.get("quantidade", 1)),
            peso_kg=float(it.get("peso_kg", 0.5)),
        )
        for it in dados.get("itens") or []
    ]
    return Pedido(
        id=dados["id"],
        cliente=dados["cliente"],
        categoria_cliente=str(dados.get("categoria_cliente", "bronze")),
        itens=itens,
        tipo_frete=str(dados.get("tipo_frete", "padrao")),
    )


def processar_pedidos(pedidos: list[dict]) -> list[dict]:
    """Converte pedidos brutos em modelos e retorna seus resumos, na mesma ordem."""
    return [_pedido_de_dict(p).para_dict() for p in pedidos]
