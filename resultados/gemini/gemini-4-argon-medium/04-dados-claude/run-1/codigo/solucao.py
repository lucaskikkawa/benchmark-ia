import csv
import json
import math
from pathlib import Path

REQUIRED_COLUMNS = {
    "data",
    "regiao",
    "produto",
    "quantidade",
    "preco_unitario",
    "status",
}


def resumir_vendas(entrada: str | Path, saida: str | Path) -> dict:
    entrada_path = Path(entrada)
    saida_path = Path(saida)

    with entrada_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        try:
            raw_header = next(reader)
        except StopIteration:
            raise ValueError("Arquivo CSV vazio ou sem cabeçalho.")

        header = [col.strip() for col in raw_header]
        col_indices = {col: idx for idx, col in enumerate(header)}

        if not REQUIRED_COLUMNS.issubset(col_indices.keys()):
            raise ValueError("Faltam colunas obrigatórias no cabeçalho.")

        num_cols = len(header)
        idx_regiao = col_indices["regiao"]
        idx_produto = col_indices["produto"]
        idx_quantidade = col_indices["quantidade"]
        idx_preco = col_indices["preco_unitario"]
        idx_status = col_indices["status"]

        linhas_invalidas = 0
        agregado: dict[str, dict] = {}

        for row in reader:
            if not row or (len(row) == 1 and row[0].strip() == ""):
                continue

            if len(row) != num_cols:
                linhas_invalidas += 1
                continue

            regiao = row[idx_regiao].strip()
            produto = row[idx_produto].strip()
            q_str = row[idx_quantidade].strip()
            p_str = row[idx_preco].strip()
            status = row[idx_status].strip()

            if not regiao or not produto:
                linhas_invalidas += 1
                continue

            try:
                quantidade = int(q_str)
            except ValueError:
                linhas_invalidas += 1
                continue

            if quantidade <= 0:
                linhas_invalidas += 1
                continue

            try:
                preco = float(p_str)
            except ValueError:
                linhas_invalidas += 1
                continue

            if not math.isfinite(preco) or preco < 0:
                linhas_invalidas += 1
                continue

            if status.lower() != "concluida":
                continue

            if regiao not in agregado:
                agregado[regiao] = {
                    "quantidade_total": 0,
                    "total_vendas": 0.0,
                    "produtos": {},
                }

            reg_info = agregado[regiao]
            reg_info["quantidade_total"] += quantidade
            reg_info["total_vendas"] += quantidade * preco
            reg_info["produtos"][produto] = (
                reg_info["produtos"].get(produto, 0) + quantidade
            )

    regioes_out = {}
    for regiao in sorted(agregado.keys()):
        reg_info = agregado[regiao]
        produtos = reg_info["produtos"]
        produto_mais_vendido = min(
            produtos.items(), key=lambda item: (-item[1], item[0])
        )[0]
        regioes_out[regiao] = {
            "quantidade_total": int(reg_info["quantidade_total"]),
            "total_vendas": float(round(reg_info["total_vendas"], 2)),
            "produto_mais_vendido": produto_mais_vendido,
        }

    total_geral = float(
        round(sum(r["total_vendas"] for r in regioes_out.values()), 2)
    )

    resultado = {
        "regioes": regioes_out,
        "total_geral": total_geral,
        "linhas_invalidas": int(linhas_invalidas),
    }

    saida_path.parent.mkdir(parents=True, exist_ok=True)
    with saida_path.open("w", encoding="utf-8") as f_out:
        json.dump(resultado, f_out, ensure_ascii=False, indent=2)

    return resultado
