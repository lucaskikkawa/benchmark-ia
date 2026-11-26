from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from pathlib import Path

COLUNAS_OBRIGATORIAS = frozenset(
    {"data", "regiao", "produto", "quantidade", "preco_unitario", "status"}
)


def resumir_vendas(entrada: str | Path, saida: str | Path) -> dict:
    entrada_path = Path(entrada)

    with entrada_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header is None:
            raise ValueError("Arquivo CSV vazio: cabeçalho ausente.")

        num_colunas = len(header)
        indices = {col.strip(): idx for idx, col in enumerate(header)}
        faltantes = COLUNAS_OBRIGATORIAS - indices.keys()
        if faltantes:
            raise ValueError(
                f"Colunas obrigatórias ausentes: {', '.join(sorted(faltantes))}."
            )

        idx_regiao = indices["regiao"]
        idx_produto = indices["produto"]
        idx_quantidade = indices["quantidade"]
        idx_preco = indices["preco_unitario"]
        idx_status = indices["status"]

        linhas_invalidas = 0
        quantidades_por_regiao: dict[str, int] = defaultdict(int)
        totais_por_regiao: dict[str, float] = defaultdict(float)
        produtos_por_regiao: dict[str, dict[str, int]] = defaultdict(
            lambda: defaultdict(int)
        )

        for row in reader:
            if not row or (len(row) == 1 and not row[0].strip()):
                continue

            if len(row) != num_colunas:
                linhas_invalidas += 1
                continue

            valores = [campo.strip() for campo in row]
            regiao = valores[idx_regiao]
            produto = valores[idx_produto]
            quantidade_str = valores[idx_quantidade]
            preco_str = valores[idx_preco]
            status = valores[idx_status]

            if not regiao or not produto:
                linhas_invalidas += 1
                continue

            try:
                quantidade = int(quantidade_str)
            except ValueError:
                linhas_invalidas += 1
                continue

            if quantidade <= 0:
                linhas_invalidas += 1
                continue

            try:
                preco_unitario = float(preco_str)
            except ValueError:
                linhas_invalidas += 1
                continue

            if not math.isfinite(preco_unitario) or preco_unitario < 0:
                linhas_invalidas += 1
                continue

            if status.lower() != "concluida":
                continue

            quantidades_por_regiao[regiao] += quantidade
            totais_por_regiao[regiao] += quantidade * preco_unitario
            produtos_por_regiao[regiao][produto] += quantidade

    regioes: dict[str, dict[str, int | float | str]] = {}
    for regiao in sorted(quantidades_por_regiao):
        total_vendas = float(round(totais_por_regiao[regiao], 2))
        if total_vendas == 0.0:
            total_vendas = 0.0
        produto_mais_vendido = min(
            produtos_por_regiao[regiao].items(),
            key=lambda item: (-item[1], item[0]),
        )[0]
        regioes[regiao] = {
            "quantidade_total": int(quantidades_por_regiao[regiao]),
            "total_vendas": total_vendas,
            "produto_mais_vendido": produto_mais_vendido,
        }

    total_geral = float(round(sum(r["total_vendas"] for r in regioes.values()), 2))
    if total_geral == 0.0:
        total_geral = 0.0

    resumo = {
        "regioes": regioes,
        "total_geral": total_geral,
        "linhas_invalidas": int(linhas_invalidas),
    }

    saida_path = Path(saida)
    saida_path.parent.mkdir(parents=True, exist_ok=True)
    with saida_path.open("w", encoding="utf-8") as f:
        json.dump(resumo, f, ensure_ascii=False, indent=2)

    return resumo
