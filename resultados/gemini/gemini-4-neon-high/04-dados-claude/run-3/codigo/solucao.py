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


def resumir_vendas(entrada: str | Path, saida: str | Path) -> dict:
    """Lê um CSV de vendas, agrega os dados, grava o resumo em JSON e retorna o dict."""
    entrada_path = Path(entrada)
    saida_path = Path(saida)

    linhas_invalidas = 0
    quantidades_por_regiao: dict[str, int] = defaultdict(int)
    vendas_por_regiao: dict[str, float] = defaultdict(float)
    produtos_por_regiao: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    with entrada_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f, delimiter=",", quotechar='"', skipinitialspace=True)
        header = next(reader, None)
        if header is None:
            raise ValueError("Arquivo CSV vazio ou sem cabeçalho.")

        num_cols = len(header)
        col_indices: dict[str, int] = {}
        for idx, col in enumerate(header):
            nome = col.strip()
            if nome not in col_indices:
                col_indices[nome] = idx

        faltando = [col for col in REQUIRED_COLUMNS if col not in col_indices]
        if faltando:
            raise ValueError(f"Colunas obrigatórias ausentes: {', '.join(faltando)}")

        idx_regiao = col_indices["regiao"]
        idx_produto = col_indices["produto"]
        idx_quantidade = col_indices["quantidade"]
        idx_preco = col_indices["preco_unitario"]
        idx_status = col_indices["status"]

        for row in reader:
            stripped = [campo.strip() for campo in row]
            if not any(stripped):
                continue

            if len(stripped) != num_cols:
                linhas_invalidas += 1
                continue

            regiao = stripped[idx_regiao]
            produto = stripped[idx_produto]
            qtd_str = stripped[idx_quantidade]
            preco_str = stripped[idx_preco]
            status = stripped[idx_status]

            if not regiao or not produto:
                linhas_invalidas += 1
                continue

            try:
                quantidade = int(qtd_str)
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
            vendas_por_regiao[regiao] += quantidade * preco_unitario
            produtos_por_regiao[regiao][produto] += quantidade

    regioes: dict[str, dict[str, int | float | str]] = {}
    for regiao in sorted(quantidades_por_regiao):
        total_vendas = float(round(vendas_por_regiao[regiao], 2)) + 0.0
        produto_mais_vendido = min(
            produtos_por_regiao[regiao].items(),
            key=lambda item: (-item[1], item[0]),
        )[0]
        regioes[regiao] = {
            "quantidade_total": int(quantidades_por_regiao[regiao]),
            "total_vendas": total_vendas,
            "produto_mais_vendido": produto_mais_vendido,
        }

    total_geral = float(round(sum(info["total_vendas"] for info in regioes.values()), 2)) + 0.0

    resumo = {
        "regioes": regioes,
        "total_geral": total_geral,
        "linhas_invalidas": int(linhas_invalidas),
    }

    saida_path.parent.mkdir(parents=True, exist_ok=True)
    with saida_path.open("w", encoding="utf-8") as f:
        json.dump(resumo, f, ensure_ascii=False, indent=2)

    return resumo
