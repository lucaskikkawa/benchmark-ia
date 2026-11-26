from __future__ import annotations

import csv
import json
import math
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
    entrada_path = Path(entrada)
    saida_path = Path(saida)

    linhas_invalidas = 0
    acumulador: dict[str, dict[str, object]] = {}

    with entrada_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header is None:
            raise ValueError("Arquivo CSV vazio: cabeçalho ausente.")

        num_colunas = len(header)
        col_indices: dict[str, int] = {}
        for idx, col_name in enumerate(header):
            name = col_name.strip()
            if name not in col_indices:
                col_indices[name] = idx

        faltando = [col for col in REQUIRED_COLUMNS if col not in col_indices]
        if faltando:
            raise ValueError(
                f"Colunas obrigatórias ausentes no cabeçalho: {', '.join(faltando)}"
            )

        idx_regiao = col_indices["regiao"]
        idx_produto = col_indices["produto"]
        idx_quantidade = col_indices["quantidade"]
        idx_preco = col_indices["preco_unitario"]
        idx_status = col_indices["status"]

        for row in reader:
            valores = [v.strip() for v in row]
            if not any(valores):
                continue

            if len(valores) != num_colunas:
                linhas_invalidas += 1
                continue

            regiao = valores[idx_regiao]
            produto = valores[idx_produto]
            qtd_str = valores[idx_quantidade]
            preco_str = valores[idx_preco]
            status = valores[idx_status]

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

            if regiao not in acumulador:
                acumulador[regiao] = {
                    "quantidade_total": 0,
                    "total_vendas": 0.0,
                    "produtos": {},
                }

            dados_regiao = acumulador[regiao]
            dados_regiao["quantidade_total"] += quantidade
            dados_regiao["total_vendas"] += quantidade * preco_unitario
            produtos: dict[str, int] = dados_regiao["produtos"]
            produtos[produto] = produtos.get(produto, 0) + quantidade

    regioes: dict[str, dict[str, int | float | str]] = {}
    for regiao in sorted(acumulador):
        dados = acumulador[regiao]
        produtos = dados["produtos"]
        produto_mais_vendido = min(
            produtos.items(), key=lambda item: (-item[1], item[0])
        )[0]
        total_vendas = float(round(dados["total_vendas"] + 0.0, 2))
        regioes[regiao] = {
            "quantidade_total": int(dados["quantidade_total"]),
            "total_vendas": total_vendas,
            "produto_mais_vendido": produto_mais_vendido,
        }

    total_geral = float(
        round(sum((r["total_vendas"] for r in regioes.values()), 0.0), 2)
    )

    resultado = {
        "regioes": regioes,
        "total_geral": total_geral,
        "linhas_invalidas": int(linhas_invalidas),
    }

    saida_path.parent.mkdir(parents=True, exist_ok=True)
    with saida_path.open("w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    return resultado
