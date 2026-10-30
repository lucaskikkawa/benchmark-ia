"""Entidades e regras de cálculo para o processamento de pedidos."""

from dataclasses import dataclass, field


__all__ = [
    "ItemPedido",
    "CalculadoraFrete",
    "CalculadoraDesconto",
    "Pedido",
    "processar_pedidos",
]


@dataclass
class ItemPedido:
    nome: str
    preco: float
    quantidade: int = 1
    peso_kg: float = 0.5

    def __post_init__(self) -> None:
        if self.preco < 0.0:
            raise ValueError("O preço deve ser maior ou igual a zero.")
        if self.quantidade < 1:
            raise ValueError("A quantidade deve ser maior ou igual a um.")
        if self.peso_kg < 0.0:
            raise ValueError("O peso deve ser maior ou igual a zero.")

    @property
    def subtotal(self) -> float:
        return round(self.preco * self.quantidade, 2)

    @property
    def peso_total(self) -> float:
        return round(self.peso_kg * self.quantidade, 3)


class CalculadoraFrete:
    @staticmethod
    def calcular(tipo: str, peso_kg: float, valor_total: float) -> float:
        if valor_total < 0.0 or peso_kg < 0.0:
            raise ValueError("O valor total e o peso devem ser não negativos.")
        if valor_total >= 200.0:
            return 0.0

        tarifas = {
            "padrao": (10.0, 1.5),
            "expresso": (25.0, 3.0),
            "economico": (5.0, 0.8),
        }
        tipo_normalizado = tipo.lower()
        if tipo_normalizado not in tarifas:
            raise ValueError(f"Tipo de frete desconhecido: {tipo}")
        valor_base, valor_por_kg = tarifas[tipo_normalizado]
        return round(valor_base + peso_kg * valor_por_kg, 2)


class CalculadoraDesconto:
    @staticmethod
    def calcular(categoria_cliente: str, valor_total: float) -> float:
        if valor_total < 0.0:
            raise ValueError("O valor total deve ser maior ou igual a zero.")

        categoria = categoria_cliente.lower()
        if categoria == "prata" and valor_total >= 100.0:
            return round(0.05 * valor_total, 2)
        if categoria == "ouro":
            taxa = 0.10 if valor_total >= 50.0 else 0.05
            return round(taxa * valor_total, 2)
        if categoria == "vip":
            return round(0.15 * valor_total, 2)
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
        return CalculadoraDesconto.calcular(
            self.categoria_cliente, self.calcular_total_itens()
        )

    def calcular_frete(self) -> float:
        return CalculadoraFrete.calcular(
            self.tipo_frete,
            self.calcular_peso_total(),
            self.calcular_total_itens(),
        )

    def calcular_total_final(self) -> float:
        return round(
            self.calcular_total_itens()
            - self.calcular_desconto()
            + self.calcular_frete(),
            2,
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


def processar_pedidos(pedidos: list[dict]) -> list[dict]:
    """Converte os pedidos brutos em entidades e preserva a ordem recebida."""
    resultados = []
    for dados in pedidos:
        itens = [
            ItemPedido(
                nome=item["nome"],
                preco=float(item["preco"]),
                quantidade=int(item.get("quantidade", 1)),
                peso_kg=float(item.get("peso_kg", 0.5)),
            )
            for item in dados.get("itens", [])
        ]
        pedido = Pedido(
            id=dados["id"],
            cliente=dados["cliente"],
            categoria_cliente=str(dados.get("categoria_cliente", "bronze")),
            itens=itens,
            tipo_frete=str(dados.get("tipo_frete", "padrao")),
        )
        resultados.append(pedido.para_dict())
    return resultados
