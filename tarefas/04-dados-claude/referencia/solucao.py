"""Resumo de vendas: lê um CSV, agrega por região e escreve um JSON."""

import csv
import json
import math
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

COLUNAS_OBRIGATORIAS = {"data", "regiao", "produto", "quantidade", "preco_unitario", "status"}
STATUS_CONCLUIDA = "concluida"


@dataclass
class _Venda:
    regiao: str
    produto: str
    quantidade: int
    preco_unitario: float
    status: str


@dataclass
class _AcumuladorRegiao:
    quantidade_total: int = 0
    total_vendas: float = 0.0
    quantidade_por_produto: Counter = field(default_factory=Counter)

    def adicionar(self, venda: _Venda) -> None:
        self.quantidade_total += venda.quantidade
        self.total_vendas += venda.quantidade * venda.preco_unitario
        self.quantidade_por_produto[venda.produto] += venda.quantidade

    def resumo(self) -> dict:
        # Maior quantidade primeiro; empate resolvido pelo nome em ordem alfabética.
        mais_vendido = min(self.quantidade_por_produto.items(), key=lambda par: (-par[1], par[0]))[0]
        return {
            "quantidade_total": self.quantidade_total,
            "total_vendas": float(round(self.total_vendas, 2)),
            "produto_mais_vendido": mais_vendido,
        }


def _converter_linha(linha: dict) -> _Venda | None:
    """Converte uma linha do CSV em _Venda, ou None se a linha for inválida."""
    # DictReader: campos a mais ficam sob a chave None; campos a menos viram None.
    if None in linha or any(valor is None for valor in linha.values()):
        return None
    valores = {chave: valor.strip() for chave, valor in linha.items()}
    try:
        quantidade = int(valores["quantidade"])
        preco = float(valores["preco_unitario"])
    except ValueError:
        return None
    if not valores["regiao"] or not valores["produto"] or quantidade <= 0:
        return None
    if not math.isfinite(preco) or preco < 0:
        return None
    return _Venda(valores["regiao"], valores["produto"], quantidade, preco, valores["status"])


def resumir_vendas(entrada: str | Path, saida: str | Path) -> dict:
    """Agrega as vendas concluídas de ``entrada`` por região e grava o resumo JSON em ``saida``."""
    acumuladores: dict[str, _AcumuladorRegiao] = {}
    linhas_invalidas = 0

    # utf-8-sig: aceita (e descarta) BOM no início do arquivo.
    with open(entrada, encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        faltando = COLUNAS_OBRIGATORIAS - {c.strip() for c in leitor.fieldnames or []}
        if faltando:
            raise ValueError(f"colunas obrigatórias ausentes: {', '.join(sorted(faltando))}")
        leitor.fieldnames = [c.strip() for c in leitor.fieldnames]

        for linha in leitor:
            venda = _converter_linha(linha)
            if venda is None:
                linhas_invalidas += 1
            elif venda.status.lower() == STATUS_CONCLUIDA:
                acumuladores.setdefault(venda.regiao, _AcumuladorRegiao()).adicionar(venda)

    regioes = {regiao: acumuladores[regiao].resumo() for regiao in sorted(acumuladores)}
    resumo = {
        "regioes": regioes,
        "total_geral": round(sum((r["total_vendas"] for r in regioes.values()), 0.0), 2),
        "linhas_invalidas": linhas_invalidas,
    }
    saida = Path(saida)
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text(json.dumps(resumo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return resumo
