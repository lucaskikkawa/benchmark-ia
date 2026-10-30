"""Processador de pedidos: cálculo de subtotal, desconto, frete e total."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "ItemPedido",
    "CalculadoraFrete",
    "CalculadoraDesconto",
    "Pedido",
    "processar_pedidos",
]


def _nao_negativo(valor: float) -> bool:
    """True se o valor é um número finito >= 0 (rejeita NaN)."""
    return isinstance(valor, (int, float)) and not math.isnan(valor) and valor >= 0


@dataclass
class ItemPedido:
    nome: str
    preco: float
    quantidade: int = 1
    peso_kg: float = 0.5

    def __post_init__(self) -> None:
        if not _nao_negativo(self.preco):
            raise ValueError(f"Preço inválido para o item '{self.nome}': {self.preco}")
        if isinstance(self.quantidade, bool) or not isinstance(self.quantidade, int) or self.quantidade < 1:
            raise ValueError(f"Quantidade inválida para o item '{self.nome}': {self.quantidade}")
        if not _nao_negativo(self.peso_kg):
            raise ValueError(f"Peso inválido para o item '{self.nome}': {self.peso_kg}")

    @property
    def subtotal(self) -> float:
        return round(self.preco * self.quantidade, 2)

    @property
    def peso_total(self) -> float:
        return round(self.peso_kg * self.quantidade, 3)


class CalculadoraFrete:
    LIMITE_FRETE_GRATIS = 200.0
    TABELA: dict[str, tuple[float, float]] = {
        # tipo: (taxa fixa, custo por kg)
        "padrao": (10.0, 1.5),
        "expresso": (25.0, 3.0),
        "economico": (5.0, 0.8),
    }

    @classmethod
    def calcular(cls, tipo: str, peso_kg: float, valor_total: float) -> float:
        if not _nao_negativo(valor_total) or not _nao_negativo(peso_kg):
            raise ValueError("Peso e valor total devem ser não negativos.")
        if valor_total >= cls.LIMITE_FRETE_GRATIS:
            return 0.0
        tarifa = cls.TABELA.get(str(tipo).lower())
        if tarifa is None:
            raise ValueError(f"Tipo de frete desconhecido: {tipo}")
        fixo, por_kg = tarifa
        return round(fixo + peso_kg * por_kg, 2)


class CalculadoraDesconto:
    @staticmethod
    def calcular(categoria_cliente: str, valor_total: float) -> float:
        if not _nao_negativo(valor_total):
            raise ValueError("Valor total deve ser não negativo.")
        categoria = str(categoria_cliente).lower()
        if categoria == "prata":
            return round(0.05 * valor_total, 2) if valor_total >= 100.0 else 0.0
        if categoria == "ouro":
            taxa = 0.10 if valor_total >= 50.0 else 0.05
            return round(taxa * valor_total, 2)
        if categoria == "vip":
            return round(0.15 * valor_total, 2)
        return 0.0  # bronze e categorias desconhecidas


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
        return round(self.calcular_total_itens() - self.calcular_desconto() + self.calcular_frete(), 2)

    def para_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "cliente": self.cliente,
            "subtotal": self.calcular_total_itens(),
            "desconto": self.calcular_desconto(),
            "frete": self.calcular_frete(),
            "total": self.calcular_total_final(),
        }


def _criar_item(dados: dict[str, Any]) -> ItemPedido:
    return ItemPedido(
        nome=str(dados.get("nome", "")),
        preco=float(dados["preco"]),
        quantidade=int(dados.get("quantidade", 1)),
        peso_kg=float(dados.get("peso_kg", 0.5)),
    )


def _criar_pedido(dados: dict[str, Any]) -> Pedido:
    return Pedido(
        id=dados["id"],
        cliente=dados["cliente"],
        categoria_cliente=str(dados.get("categoria_cliente", "bronze")),
        itens=[_criar_item(item) for item in (dados.get("itens") or [])],
        tipo_frete=str(dados.get("tipo_frete", "padrao")),
    )


def processar_pedidos(pedidos: list[dict]) -> list[dict]:
    return [_criar_pedido(dados).para_dict() for dados in pedidos]
