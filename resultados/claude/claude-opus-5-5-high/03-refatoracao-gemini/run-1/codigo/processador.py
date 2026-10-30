"""Processamento de pedidos: cálculo de subtotal, desconto, frete e total."""

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


def _validar_numero(nome: str, valor: float, minimo: float) -> None:
    """Levanta ValueError se `valor` não for um número finito >= `minimo`."""
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(f"{nome} deve ser numérico: {valor!r}")
    if math.isnan(valor) or math.isinf(valor) or valor < minimo:
        raise ValueError(f"{nome} inválido: {valor!r}")


@dataclass
class ItemPedido:
    nome: str
    preco: float
    quantidade: int = 1
    peso_kg: float = 0.5

    def __post_init__(self) -> None:
        _validar_numero("preco", self.preco, 0.0)
        _validar_numero("peso_kg", self.peso_kg, 0.0)
        if isinstance(self.quantidade, bool) or not isinstance(self.quantidade, int):
            raise ValueError(f"quantidade deve ser inteira: {self.quantidade!r}")
        if self.quantidade < 1:
            raise ValueError(f"quantidade inválida: {self.quantidade!r}")

    @property
    def subtotal(self) -> float:
        return round(self.preco * self.quantidade, 2)

    @property
    def peso_total(self) -> float:
        return round(self.peso_kg * self.quantidade, 3)


class CalculadoraFrete:
    LIMITE_FRETE_GRATIS = 200.0
    # tipo -> (taxa fixa, custo por kg)
    TABELA: dict[str, tuple[float, float]] = {
        "padrao": (10.0, 1.5),
        "expresso": (25.0, 3.0),
        "economico": (5.0, 0.8),
    }

    @classmethod
    def calcular(cls, tipo: str, peso_kg: float, valor_total: float) -> float:
        if valor_total < 0 or peso_kg < 0:
            raise ValueError("Peso e valor total não podem ser negativos")
        if valor_total >= cls.LIMITE_FRETE_GRATIS:
            return 0.0
        tarifa = cls.TABELA.get(str(tipo).lower())
        if tarifa is None:
            raise ValueError(f"Tipo de frete desconhecido: {tipo}")
        taxa_fixa, custo_kg = tarifa
        return round(taxa_fixa + peso_kg * custo_kg, 2)


class CalculadoraDesconto:
    @staticmethod
    def calcular(categoria_cliente: str, valor_total: float) -> float:
        if valor_total < 0:
            raise ValueError("Valor total não pode ser negativo")
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
        return round(float(sum(item.subtotal for item in self.itens)), 2)

    def calcular_peso_total(self) -> float:
        return round(float(sum(item.peso_total for item in self.itens)), 3)

    def calcular_desconto(self) -> float:
        return CalculadoraDesconto.calcular(
            self.categoria_cliente, self.calcular_total_itens()
        )

    def calcular_frete(self) -> float:
        return CalculadoraFrete.calcular(
            self.tipo_frete, self.calcular_peso_total(), self.calcular_total_itens()
        )

    def calcular_total_final(self) -> float:
        total_itens = self.calcular_total_itens()
        return round(total_itens - self.calcular_desconto() + self.calcular_frete(), 2)

    def para_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "cliente": self.cliente,
            "subtotal": self.calcular_total_itens(),
            "desconto": self.calcular_desconto(),
            "frete": self.calcular_frete(),
            "total": self.calcular_total_final(),
        }


def _item_de_dict(dados: dict[str, Any]) -> ItemPedido:
    kwargs: dict[str, Any] = {
        "nome": str(dados.get("nome", "")),
        "preco": float(dados["preco"]),
    }
    if dados.get("quantidade") is not None:
        kwargs["quantidade"] = int(dados["quantidade"])
    if dados.get("peso_kg") is not None:
        kwargs["peso_kg"] = float(dados["peso_kg"])
    return ItemPedido(**kwargs)


def _pedido_de_dict(dados: dict[str, Any]) -> Pedido:
    kwargs: dict[str, Any] = {
        "id": dados["id"],
        "cliente": dados["cliente"],
        "itens": [_item_de_dict(it) for it in (dados.get("itens") or [])],
    }
    if dados.get("categoria_cliente") is not None:
        kwargs["categoria_cliente"] = str(dados["categoria_cliente"])
    if dados.get("tipo_frete") is not None:
        kwargs["tipo_frete"] = str(dados["tipo_frete"])
    return Pedido(**kwargs)


def processar_pedidos(pedidos: list[dict]) -> list[dict]:
    return [_pedido_de_dict(p).para_dict() for p in pedidos]
