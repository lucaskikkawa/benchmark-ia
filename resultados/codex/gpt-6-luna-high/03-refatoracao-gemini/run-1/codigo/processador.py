from dataclasses import dataclass, field


@dataclass
class ItemPedido:
    nome: str
    preco: float
    quantidade: int = 1
    peso_kg: float = 0.5

    def __post_init__(self) -> None:
        if not self.preco >= 0.0:
            raise ValueError("preco deve ser maior ou igual a 0.0")
        if self.quantidade < 1:
            raise ValueError("quantidade deve ser maior ou igual a 1")
        if not self.peso_kg >= 0.0:
            raise ValueError("peso_kg deve ser maior ou igual a 0.0")

    @property
    def subtotal(self) -> float:
        return round(self.preco * self.quantidade, 2)

    @property
    def peso_total(self) -> float:
        return round(self.peso_kg * self.quantidade, 3)


class CalculadoraFrete:
    @staticmethod
    def calcular(tipo: str, peso_kg: float, valor_total: float) -> float:
        if valor_total < 0:
            raise ValueError("valor_total deve ser maior ou igual a 0")
        if peso_kg < 0:
            raise ValueError("peso_kg deve ser maior ou igual a 0")
        if valor_total >= 200.0:
            return 0.0

        tipo_normalizado = tipo.lower()
        if tipo_normalizado == "padrao":
            return round(10.0 + peso_kg * 1.5, 2)
        if tipo_normalizado == "expresso":
            return round(25.0 + peso_kg * 3.0, 2)
        if tipo_normalizado == "economico":
            return round(5.0 + peso_kg * 0.8, 2)
        raise ValueError(f"Tipo de frete desconhecido: {tipo}")


class CalculadoraDesconto:
    @staticmethod
    def calcular(categoria_cliente: str, valor_total: float) -> float:
        if valor_total < 0:
            raise ValueError("valor_total deve ser maior ou igual a 0")

        categoria = categoria_cliente.lower()
        if categoria == "bronze":
            return 0.0
        if categoria == "prata":
            return round(0.05 * valor_total, 2) if valor_total >= 100.0 else 0.0
        if categoria == "ouro":
            percentual = 0.10 if valor_total >= 50.0 else 0.05
            return round(percentual * valor_total, 2)
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
        return round(sum(item.subtotal for item in self.itens), 2)

    def calcular_peso_total(self) -> float:
        return round(sum(item.peso_total for item in self.itens), 3)

    def calcular_desconto(self) -> float:
        return CalculadoraDesconto.calcular(
            self.categoria_cliente, self.calcular_total_itens()
        )

    def calcular_frete(self) -> float:
        return CalculadoraFrete.calcular(
            self.tipo_frete, self.calcular_peso_total(), self.calcular_total_itens()
        )

    def calcular_total_final(self) -> float:
        return round(
            self.calcular_total_itens() - self.calcular_desconto() + self.calcular_frete(),
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
    resultado = []
    for dados_pedido in pedidos:
        itens = [
            ItemPedido(
                nome=dados_item["nome"],
                preco=float(dados_item["preco"]),
                quantidade=int(dados_item.get("quantidade", 1)),
                peso_kg=float(dados_item.get("peso_kg", 0.5)),
            )
            for dados_item in dados_pedido.get("itens", [])
        ]
        pedido = Pedido(
            id=dados_pedido["id"],
            cliente=dados_pedido["cliente"],
            categoria_cliente=dados_pedido.get("categoria_cliente", "bronze"),
            itens=itens,
            tipo_frete=dados_pedido.get("tipo_frete", "padrao"),
        )
        resultado.append(pedido.para_dict())
    return resultado
