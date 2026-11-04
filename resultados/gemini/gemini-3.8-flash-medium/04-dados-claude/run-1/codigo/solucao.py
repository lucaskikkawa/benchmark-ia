import csv
import json
import math
from pathlib import Path


def resumir_vendas(entrada: str | Path, saida: str | Path) -> dict:
    required_columns = ["data", "regiao", "produto", "quantidade", "preco_unitario", "status"]

    with open(entrada, mode="r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)

        header = None
        for row in reader:
            if not row or (len(row) == 1 and not row[0].strip()):
                continue
            header = [col.strip() for col in row]
            break

        if header is None:
            raise ValueError("Arquivo CSV vazio ou sem cabeçalho.")

        for col in required_columns:
            if col not in header:
                raise ValueError(f"Coluna obrigatória ausente no cabeçalho: '{col}'.")

        col_indices = {col: header.index(col) for col in required_columns}

        linhas_invalidas = 0
        regioes_data = {}

        for row in reader:
            if not row or (len(row) == 1 and not row[0].strip()):
                continue

            if len(row) != len(header):
                linhas_invalidas += 1
                continue

            row = [val.strip() for val in row]

            regiao = row[col_indices["regiao"]]
            produto = row[col_indices["produto"]]
            qtd_str = row[col_indices["quantidade"]]
            preco_str = row[col_indices["preco_unitario"]]
            status_str = row[col_indices["status"]]

            if not regiao or not produto:
                linhas_invalidas += 1
                continue

            try:
                quantidade = int(qtd_str)
                if quantidade <= 0:
                    linhas_invalidas += 1
                    continue
            except ValueError:
                linhas_invalidas += 1
                continue

            try:
                preco_unitario = float(preco_str)
                if not math.isfinite(preco_unitario) or preco_unitario < 0:
                    linhas_invalidas += 1
                    continue
                if preco_unitario == 0.0:
                    preco_unitario = 0.0
            except ValueError:
                linhas_invalidas += 1
                continue

            if status_str.lower() != "concluida":
                continue

            if regiao not in regioes_data:
                regioes_data[regiao] = {
                    "quantidade_total": 0,
                    "total_vendas_raw": 0.0,
                    "produtos": {},
                }

            regioes_data[regiao]["quantidade_total"] += quantidade
            regioes_data[regiao]["total_vendas_raw"] += quantidade * preco_unitario
            regioes_data[regiao]["produtos"][produto] = (
                regioes_data[regiao]["produtos"].get(produto, 0) + quantidade
            )

    regioes_resumo = {}
    for reg in sorted(regioes_data.keys()):
        info = regioes_data[reg]
        # In case of tie in quantity, select the alphabetically smaller product name
        best_product = min(info["produtos"].keys(), key=lambda p: (-info["produtos"][p], p))
        regioes_resumo[reg] = {
            "quantidade_total": int(info["quantidade_total"]),
            "total_vendas": float(round(info["total_vendas_raw"], 2)),
            "produto_mais_vendido": str(best_product),
        }

    total_geral = float(round(sum(r["total_vendas"] for r in regioes_resumo.values()), 2))

    resultado = {
        "regioes": regioes_resumo,
        "total_geral": total_geral,
        "linhas_invalidas": int(linhas_invalidas),
    }

    saida_path = Path(saida)
    saida_path.parent.mkdir(parents=True, exist_ok=True)
    with open(saida_path, mode="w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    return resultado
