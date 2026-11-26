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


def _round_money(value: float) -> float:
    rounded = float(round(value, 2))
    return 0.0 if rounded == 0 else rounded


def resumir_vendas(entrada: str | Path, saida: str | Path) -> dict:
    """Lê um CSV de vendas, agrega por região, escreve JSON em `saida` e retorna o resumo."""
    entrada_path = Path(entrada)
    saida_path = Path(saida)

    with entrada_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        raw_header = next(reader, None)
        if raw_header is None:
            raise ValueError("Arquivo CSV vazio: cabeçalho ausente.")

        header = [col.strip() for col in raw_header]
        col_indices: dict[str, int] = {}
        for idx, name in enumerate(header):
            if name not in col_indices:
                col_indices[name] = idx

        missing = [col for col in REQUIRED_COLUMNS if col not in col_indices]
        if missing:
            raise ValueError(f"Colunas obrigatórias ausentes: {', '.join(missing)}")

        expected_len = len(header)
        idx_regiao = col_indices["regiao"]
        idx_produto = col_indices["produto"]
        idx_quantidade = col_indices["quantidade"]
        idx_preco = col_indices["preco_unitario"]
        idx_status = col_indices["status"]

        linhas_invalidas = 0
        totais_regiao: dict[str, list] = {}

        for raw_row in reader:
            row = [val.strip() for val in raw_row]
            if all(val == "" for val in row):
                continue

            if len(row) != expected_len:
                linhas_invalidas += 1
                continue

            regiao = row[idx_regiao]
            produto = row[idx_produto]
            if not regiao or not produto:
                linhas_invalidas += 1
                continue

            try:
                quantidade = int(row[idx_quantidade])
                preco_unitario = float(row[idx_preco])
            except ValueError:
                linhas_invalidas += 1
                continue

            if quantidade <= 0 or not math.isfinite(preco_unitario) or preco_unitario < 0:
                linhas_invalidas += 1
                continue

            if row[idx_status].lower() != "concluida":
                continue

            if regiao not in totais_regiao:
                totais_regiao[regiao] = [0, 0.0, defaultdict(int)]

            agg = totais_regiao[regiao]
            agg[0] += quantidade
            agg[1] += quantidade * preco_unitario
            agg[2][produto] += quantidade

    regioes: dict[str, dict] = {}
    for regiao in sorted(totais_regiao):
        qtd_total, total_vendas, produtos = totais_regiao[regiao]
        produto_mais_vendido = min(
            produtos.items(), key=lambda item: (-item[1], item[0])
        )[0]
        regioes[regiao] = {
            "quantidade_total": int(qtd_total),
            "total_vendas": _round_money(total_vendas),
            "produto_mais_vendido": produto_mais_vendido,
        }

    total_geral = _round_money(
        sum((info["total_vendas"] for info in regioes.values()), 0.0)
    )

    resumo = {
        "regioes": regioes,
        "total_geral": total_geral,
        "linhas_invalidas": int(linhas_invalidas),
    }

    saida_path.parent.mkdir(parents=True, exist_ok=True)
    with saida_path.open("w", encoding="utf-8") as f:
        json.dump(resumo, f, ensure_ascii=False, indent=2)

    return resumo
