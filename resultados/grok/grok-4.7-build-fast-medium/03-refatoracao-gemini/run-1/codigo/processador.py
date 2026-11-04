"""Processamento de pedidos com entidades, frete e desconto separados."""

from dataclasses import dataclass, field


@dataclass
class ItemPedido:
    nome: str
    preco: float
    quantidade: int = 1
    peso_kg: float = 0.5

    def __post_init__(self) -> None:
        self.preco = float(self.preco)
        self.quantidade = int(self.quantidade)
        self.peso_kg = float(self.peso_kg)
        if self.preco < 0.0:
            raise ValueError("preco deve ser >= 0.0")
        if self.quantidade < 1:
            raise ValueError("quantidade deve ser >= 1")
        if self.peso_kg < 0.0:
            raise ValueError("peso_kg deve ser >= 0.0")

    @property
    def subtotal(self) -> float:
        return round(self.preco * self.quantidade, 2)

    @property
    def peso_total(self) -> float:
        return round(self.peso_kg * self.quantidade, 3)


class CalculadoraFrete:
    @staticmethod
    def calcular(tipo: str, peso_kg: float, valor_total: float) -> float:
        if valor_total < 0 or peso_kg < 0:
            raise ValueError("valor_total e peso_kg devem ser >= 0")
        if valor_total >= 200.0:
            return 0.0
        tipo_norm = str(tipo).lower()
        if tipo_norm == "padrao":
            return round(10.0 + peso_kg * 1.5, 2)
        if tipo_norm == "expresso":
            return round(25.0 + peso_kg * 3.0, 2)
        if tipo_norm == "economico":
            return round(5.0 + peso_kg * 0.8, 2)
        raise ValueError(f"Tipo de frete desconhecido: {tipo}")


class CalculadoraDesconto:
    @staticmethod
    def calcular(categoria_cliente: str, valor_total: float) -> float:
        if valor_total < 0:
            raise ValueError("valor_total deve ser >= 0")
        cat = str(categoria_cliente).lower()
        if cat == "prata":
            if valor_total >= 100.0:
                return round(0.05 * valor_total, 2)
            return 0.0
        if cat == "ouro":
            if valor_total >= 50.0:
                return round(0.10 * valor_total, 2)
            return round(0.05 * valor_total, 2)
        if cat == "vip":
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
    resultado: list[dict] = []
    for bruto in pedidos:
        itens_brutos = bruto.get("itens") or []
        itens = [
            ItemPedido(
                nome=item["nome"],
                preco=item["preco"],
                quantidade=item.get("quantidade", 1),
                peso_kg=item.get("peso_kg", 0.5),
            )
            for item in itens_brutos
        ]
        pedido = Pedido(
            id=bruto["id"],
            cliente=bruto["cliente"],
            categoria_cliente=bruto.get("categoria_cliente", "bronze"),
            itens=itens,
            tipo_frete=bruto.get("tipo_frete", "padrao"),
        )
        resultado.append(pedido.para_dict())
    return resultado
