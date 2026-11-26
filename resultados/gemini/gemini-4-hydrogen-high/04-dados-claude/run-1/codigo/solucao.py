from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from pathlib import Path

REQUIRED_COLUMNS = (
    "data",
    "regiao",
    "produto",
    "quantidade",
    "preco_unitario",
    "status",
)


def _parse_valid_row(
    row: list[str], col_idx: dict[str, int]
) -> tuple[str, str, int, float, str] | None:
    """Validate and extract fields from a stripped CSV row, or return None if invalid."""
    regiao = row[col_idx["regiao"]]
    produto = row[col_idx["produto"]]
    if not regiao or not produto:
        return None

    try:
        quantidade = int(row[col_idx["quantidade"]])
    except ValueError:
        return None
    if quantidade <= 0:
        return None

    try:
        preco_unitario = float(row[col_idx["preco_unitario"]])
    except ValueError:
        return None
    if not math.isfinite(preco_unitario) or preco_unitario < 0:
        return None

    status = row[col_idx["status"]]
    return regiao, produto, quantidade, preco_unitario, status


def resumir_vendas(entrada: str | Path, saida: str | Path) -> dict:
    """Read a sales CSV file, aggregate completed sales by region, write JSON, and return it."""
    entrada_path = Path(entrada)

    regiao_qtd: dict[str, int] = defaultdict(int)
    regiao_total: dict[str, float] = defaultdict(float)
    regiao_produtos: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    linhas_invalidas = 0

    with entrada_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f, delimiter=",", quotechar='"', doublequote=True)
        header = next(reader, None)
        if header is None:
            raise ValueError("Arquivo CSV vazio ou sem cabeçalho.")

        header_stripped = [col.strip() for col in header]
        col_idx = {name: i for i, name in enumerate(header_stripped)}
        missing = [col for col in REQUIRED_COLUMNS if col not in col_idx]
        if missing:
            raise ValueError(f"Colunas obrigatórias ausentes: {', '.join(missing)}")

        expected_len = len(header_stripped)

        for raw_row in reader:
            if not raw_row:
                continue

            row = [val.strip() for val in raw_row]
            if len(row) != expected_len:
                linhas_invalidas += 1
                continue

            parsed = _parse_valid_row(row, col_idx)
            if parsed is None:
                linhas_invalidas += 1
                continue

            regiao, produto, quantidade, preco_unitario, status = parsed
            if status.lower() != "concluida":
                continue

            regiao_qtd[regiao] += quantidade
            regiao_total[regiao] += quantidade * preco_unitario
            regiao_produtos[regiao][produto] += quantidade

    regioes: dict[str, dict[str, int | float | str]] = {}
    for regiao in sorted(regiao_qtd):
        produtos = regiao_produtos[regiao]
        produto_mais_vendido = min(produtos.items(), key=lambda item: (-item[1], item[0]))[0]
        total_vendas = float(round(regiao_total[regiao], 2)) + 0.0
        regioes[regiao] = {
            "quantidade_total": int(regiao_qtd[regiao]),
            "total_vendas": total_vendas,
            "produto_mais_vendido": produto_mais_vendido,
        }

    total_geral = float(round(sum((r["total_vendas"] for r in regioes.values()), 0.0), 2)) + 0.0
    resultado = {
        "regioes": regioes,
        "total_geral": total_geral,
        "linhas_invalidas": int(linhas_invalidas),
    }

    saida_path = Path(saida)
    saida_path.parent.mkdir(parents=True, exist_ok=True)
    with saida_path.open("w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    return resultado
