from dataclasses import dataclass, field


@dataclass
class ItemPedido:
    nome: str
    preco: float
    quantidade: int = 1
    peso_kg: float = 0.5

    def __post_init__(self) -> None:
        self.preco = float(self.preco)
        self.peso_kg = float(self.peso_kg)
        if isinstance(self.quantidade, bool) or not isinstance(self.quantidade, (int, float)):
            raise ValueError("quantidade deve ser um inteiro >= 1")
        if isinstance(self.quantidade, float) and not self.quantidade.is_integer():
            raise ValueError("quantidade deve ser um inteiro >= 1")
        self.quantidade = int(self.quantidade)
        if self.preco < 0.0 or self.quantidade < 1 or self.peso_kg < 0.0:
            raise ValueError(
                "preco >= 0.0, quantidade >= 1 e peso_kg >= 0.0 são obrigatórios"
            )

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
            raise ValueError("valor_total e peso_kg devem ser não negativos")
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
            raise ValueError("valor_total deve ser não negativo")
        categoria = str(categoria_cliente).lower()
        if categoria == "bronze":
            return 0.0
        if categoria == "prata":
            if valor_total >= 100.0:
                return round(0.05 * valor_total, 2)
            return 0.0
        if categoria == "ouro":
            if valor_total >= 50.0:
                return round(0.10 * valor_total, 2)
            return round(0.05 * valor_total, 2)
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


def _item_de_dict(dados: dict) -> ItemPedido:
    kwargs: dict = {
        "nome": dados.get("nome", ""),
        "preco": dados["preco"],
    }
    if "quantidade" in dados and dados["quantidade"] is not None:
        kwargs["quantidade"] = dados["quantidade"]
    if "peso_kg" in dados and dados["peso_kg"] is not None:
        kwargs["peso_kg"] = dados["peso_kg"]
    return ItemPedido(**kwargs)


def processar_pedidos(pedidos: list[dict]) -> list[dict]:
    resultado = []
    for dados in pedidos:
        itens_brutos = dados.get("itens") or []
        pedido_kwargs: dict = {
            "id": dados["id"],
            "cliente": dados["cliente"],
            "itens": [_item_de_dict(item) for item in itens_brutos],
        }
        if "categoria_cliente" in dados and dados["categoria_cliente"] is not None:
            pedido_kwargs["categoria_cliente"] = dados["categoria_cliente"]
        if "tipo_frete" in dados and dados["tipo_frete"] is not None:
            pedido_kwargs["tipo_frete"] = dados["tipo_frete"]
        resultado.append(Pedido(**pedido_kwargs).para_dict())
    return resultado
