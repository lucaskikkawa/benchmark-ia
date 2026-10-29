from dataclasses import dataclass, field


@dataclass
class ItemPedido:
    nome: str
    preco: float
    quantidade: int = 1
    peso_kg: float = 0.5

    def __post_init__(self) -> None:
        if self.preco < 0.0 or self.quantidade < 1 or self.peso_kg < 0.0:
            raise ValueError("Valores inválidos para ItemPedido.")

    @property
    def subtotal(self) -> float:
        return round(self.preco * self.quantidade, 2)

    @property
    def peso_total(self) -> float:
        return round(self.peso_kg * self.quantidade, 3)


class CalculadoraFrete:
    TAXAS_BASE = {
        "padrao": (10.0, 1.5),
        "expresso": (25.0, 3.0),
        "economico": (5.0, 0.8),
    }

    @classmethod
    def calcular(cls, tipo: str, peso_kg: float, valor_total: float) -> float:
        if valor_total < 0 or peso_kg < 0:
            raise ValueError("Peso ou valor total não podem ser negativos.")

        if valor_total >= 200.0:
            return 0.0

        tipo_normalizado = str(tipo).strip().lower()
        if tipo_normalizado not in cls.TAXAS_BASE:
            raise ValueError(f"Tipo de frete desconhecido: {tipo}")

        base, por_kg = cls.TAXAS_BASE[tipo_normalizado]
        return round(base + (peso_kg * por_kg), 2)


class CalculadoraDesconto:
    @classmethod
    def calcular(cls, categoria_cliente: str, valor_total: float) -> float:
        if valor_total < 0:
            raise ValueError("Valor total não pode ser negativo.")

        cat = str(categoria_cliente).strip().lower()
        if cat == "prata":
            taxa = 0.05 if valor_total >= 100.0 else 0.0
        elif cat == "ouro":
            taxa = 0.10 if valor_total >= 50.0 else 0.05
        elif cat == "vip":
            taxa = 0.15
        else:
            taxa = 0.0
        return round(valor_total * taxa, 2)


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
            self.categoria_cliente,
            self.calcular_total_itens(),
        )

    def calcular_frete(self) -> float:
        return CalculadoraFrete.calcular(
            self.tipo_frete,
            self.calcular_peso_total(),
            self.calcular_total_itens(),
        )

    def calcular_total_final(self) -> float:
        total = self.calcular_total_itens() - self.calcular_desconto() + self.calcular_frete()
        return round(total, 2)

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
    """Processa uma lista de pedidos brutos e retorna o resumo estruturado de cada pedido."""
    resultado = []
    for p in pedidos:
        itens = [
            ItemPedido(
                nome=str(it["nome"]),
                preco=float(it["preco"]),
                quantidade=int(it.get("quantidade", 1)),
                peso_kg=float(it.get("peso_kg", 0.5)),
            )
            for it in p.get("itens", [])
        ]
        pedido = Pedido(
            id=str(p["id"]),
            cliente=str(p["cliente"]),
            categoria_cliente=str(p.get("categoria_cliente", "bronze")),
            itens=itens,
            tipo_frete=str(p.get("tipo_frete", "padrao")),
        )
        resultado.append(pedido.para_dict())
    return resultado
