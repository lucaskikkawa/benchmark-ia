"""Processador de pedidos com entidades e calculadoras separadas."""

from dataclasses import dataclass, field


@dataclass
class ItemPedido:
    """Um item de um pedido, com subtotal e peso já arredondados."""

    nome: str
    preco: float
    quantidade: int = 1
    peso_kg: float = 0.5

    def __post_init__(self) -> None:
        if self.preco < 0.0:
            raise ValueError(f"preco deve ser >= 0.0: {self.preco}")
        if self.quantidade < 1:
            raise ValueError(f"quantidade deve ser >= 1: {self.quantidade}")
        if self.peso_kg < 0.0:
            raise ValueError(f"peso_kg deve ser >= 0.0: {self.peso_kg}")

    @property
    def subtotal(self) -> float:
        return float(round(self.preco * self.quantidade, 2))

    @property
    def peso_total(self) -> float:
        return float(round(self.peso_kg * self.quantidade, 3))


class CalculadoraFrete:
    """Regras de frete por tipo, peso e valor da mercadoria."""

    @staticmethod
    def calcular(tipo: str, peso_kg: float, valor_total: float) -> float:
        if valor_total < 0 or peso_kg < 0:
            raise ValueError("valor_total e peso_kg devem ser >= 0")
        if valor_total >= 200.0:
            return 0.0
        tipo_normalizado = tipo.lower()
        if tipo_normalizado == "padrao":
            return float(round(10.0 + peso_kg * 1.5, 2))
        if tipo_normalizado == "expresso":
            return float(round(25.0 + peso_kg * 3.0, 2))
        if tipo_normalizado == "economico":
            return float(round(5.0 + peso_kg * 0.8, 2))
        raise ValueError(f"Tipo de frete desconhecido: {tipo}")


class CalculadoraDesconto:
    """Regras de desconto por categoria de cliente."""

    @staticmethod
    def calcular(categoria_cliente: str, valor_total: float) -> float:
        if valor_total < 0:
            raise ValueError("valor_total deve ser >= 0")
        categoria = categoria_cliente.lower()
        if categoria == "bronze":
            return 0.0
        if categoria == "prata":
            if valor_total >= 100.0:
                return float(round(0.05 * valor_total, 2))
            return 0.0
        if categoria == "ouro":
            if valor_total >= 50.0:
                return float(round(0.10 * valor_total, 2))
            return float(round(0.05 * valor_total, 2))
        if categoria == "vip":
            return float(round(0.15 * valor_total, 2))
        return 0.0


@dataclass
class Pedido:
    """Pedido com itens, categoria do cliente e tipo de frete."""

    id: str
    cliente: str
    categoria_cliente: str = "bronze"
    itens: list[ItemPedido] = field(default_factory=list)
    tipo_frete: str = "padrao"

    def calcular_total_itens(self) -> float:
        return float(round(sum(item.subtotal for item in self.itens), 2))

    def calcular_peso_total(self) -> float:
        return float(round(sum(item.peso_total for item in self.itens), 3))

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
        return float(round(
            self.calcular_total_itens() - self.calcular_desconto() + self.calcular_frete(),
            2,
        ))

    def para_dict(self) -> dict:
        return {
            "id": self.id,
            "cliente": self.cliente,
            "subtotal": self.calcular_total_itens(),
            "desconto": self.calcular_desconto(),
            "frete": self.calcular_frete(),
            "total": self.calcular_total_final(),
        }


def _valor_ou_padrao(dados: dict, chave: str, padrao):
    if chave not in dados or dados[chave] is None:
        return padrao
    return dados[chave]


def _item_de_dict(dados: dict) -> ItemPedido:
    return ItemPedido(
        nome=_valor_ou_padrao(dados, "nome", ""),
        preco=float(dados["preco"]),
        quantidade=int(_valor_ou_padrao(dados, "quantidade", 1)),
        peso_kg=float(_valor_ou_padrao(dados, "peso_kg", 0.5)),
    )


def processar_pedidos(pedidos: list[dict]) -> list[dict]:
    """Converte pedidos brutos nas entidades e devolve o resumo de cada um."""
    resultado = []
    for dados in pedidos:
        itens_brutos = dados.get("itens") or []
        pedido = Pedido(
            id=dados["id"],
            cliente=dados["cliente"],
            categoria_cliente=_valor_ou_padrao(dados, "categoria_cliente", "bronze"),
            itens=[_item_de_dict(item) for item in itens_brutos],
            tipo_frete=_valor_ou_padrao(dados, "tipo_frete", "padrao"),
        )
        resultado.append(pedido.para_dict())
    return resultado
