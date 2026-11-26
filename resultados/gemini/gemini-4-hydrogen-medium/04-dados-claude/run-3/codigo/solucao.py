from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from pathlib import Path

COLUNAS_OBRIGATORIAS = (
    "data",
    "regiao",
    "produto",
    "quantidade",
    "preco_unitario",
    "status",
)


def _parse_linha_valida(
    row: list[str],
    indices: dict[str, int],
) -> tuple[str, str, int, float, str] | None:
    regiao = row[indices["regiao"]]
    produto = row[indices["produto"]]
    if not regiao or not produto:
        return None

    try:
        quantidade = int(row[indices["quantidade"]])
    except ValueError:
        return None
    if quantidade <= 0:
        return None

    try:
        preco_unitario = float(row[indices["preco_unitario"]])
    except ValueError:
        return None
    if not math.isfinite(preco_unitario) or preco_unitario < 0:
        return None

    status = row[indices["status"]]
    return regiao, produto, quantidade, preco_unitario, status


def resumir_vendas(entrada: str | Path, saida: str | Path) -> dict:
    """Lê um CSV de vendas, agrega os resultados por região, grava o JSON em `saida` e retorna o resumo."""
    entrada_path = Path(entrada)
    saida_path = Path(saida)

    linhas_invalidas = 0
    qtd_por_regiao: dict[str, int] = defaultdict(int)
    vendas_por_regiao: dict[str, float] = defaultdict(float)
    produtos_por_regiao: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    with entrada_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        header_raw = next(reader, None)
        if header_raw is None:
            raise ValueError("Arquivo CSV vazio: cabeçalho ausente.")

        header = [col.strip() for col in header_raw]
        indices = {col: idx for idx, col in enumerate(header)}
        faltantes = [col for col in COLUNAS_OBRIGATORIAS if col not in indices]
        if faltantes:
            raise ValueError(f"Colunas obrigatórias ausentes: {', '.join(faltantes)}")

        num_colunas = len(header)

        for row_raw in reader:
            if not row_raw:
                continue

            if len(row_raw) != num_colunas:
                linhas_invalidas += 1
                continue

            row = [val.strip() for val in row_raw]
            parsed = _parse_linha_valida(row, indices)
            if parsed is None:
                linhas_invalidas += 1
                continue

            regiao, produto, quantidade, preco_unitario, status = parsed
            if status.lower() != "concluida":
                continue

            qtd_por_regiao[regiao] += quantidade
            vendas_por_regiao[regiao] += quantidade * preco_unitario
            produtos_por_regiao[regiao][produto] += quantidade

    regioes: dict[str, dict[str, int | float | str]] = {}
    for regiao in sorted(qtd_por_regiao):
        total_vendas = float(round(vendas_por_regiao[regiao], 2))
        if total_vendas == 0.0:
            total_vendas = 0.0
        produto_mais_vendido = min(
            produtos_por_regiao[regiao].items(),
            key=lambda item: (-item[1], item[0]),
        )[0]
        regioes[regiao] = {
            "quantidade_total": int(qtd_por_regiao[regiao]),
            "total_vendas": total_vendas,
            "produto_mais_vendido": produto_mais_vendido,
        }

    total_geral = float(round(sum(r["total_vendas"] for r in regioes.values()), 2))
    if total_geral == 0.0:
        total_geral = 0.0

    resultado = {
        "regioes": regioes,
        "total_geral": total_geral,
        "linhas_invalidas": int(linhas_invalidas),
    }

    saida_path.parent.mkdir(parents=True, exist_ok=True)
    with saida_path.open("w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    return resultado
