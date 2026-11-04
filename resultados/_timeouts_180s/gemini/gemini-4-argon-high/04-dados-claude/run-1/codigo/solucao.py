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

    with open(entrada_path, mode="r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f, delimiter=",", quotechar='"')

        header_row = next(reader, None)
        if header_row is None:
            raise ValueError("Arquivo CSV vazio (sem cabeçalho).")

        header = [col.strip() for col in header_row]
        if not all(col in header for col in REQUIRED_COLUMNS):
            raise ValueError("Colunas obrigatórias ausentes no cabeçalho.")

        num_cols = len(header)
        idx_regiao = header.index("regiao")
        idx_produto = header.index("produto")
        idx_quantidade = header.index("quantidade")
        idx_preco = header.index("preco_unitario")
        idx_status = header.index("status")

        linhas_invalidas = 0
        agregado: dict[str, dict] = {}

        for row in reader:
            valores = [campo.strip() for campo in row]
            if not valores or all(v == "" for v in valores):
                continue

            if len(valores) != num_cols:
                linhas_invalidas += 1
                continue

            regiao = valores[idx_regiao]
            produto = valores[idx_produto]
            str_quantidade = valores[idx_quantidade]
            str_preco = valores[idx_preco]
            status = valores[idx_status]

            if not regiao or not produto:
                linhas_invalidas += 1
                continue

            try:
                quantidade = int(str_quantidade)
            except ValueError:
                linhas_invalidas += 1
                continue

            if quantidade <= 0:
                linhas_invalidas += 1
                continue

            try:
                preco_unitario = float(str_preco)
            except ValueError:
                linhas_invalidas += 1
                continue

            if not math.isfinite(preco_unitario) or preco_unitario < 0:
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

            info_regiao = agregado[regiao]
            info_regiao["quantidade_total"] += quantidade
            info_regiao["total_vendas"] += quantidade * preco_unitario
            produtos = info_regiao["produtos"]
            produtos[produto] = produtos.get(produto, 0) + quantidade

    regioes: dict[str, dict] = {}
    for regiao in sorted(agregado.keys()):
        info = agregado[regiao]
        produtos = info["produtos"]
        produto_mais_vendido = min(
            produtos.items(), key=lambda item: (-item[1], item[0])
        )[0]
        regioes[regiao] = {
            "quantidade_total": int(info["quantidade_total"]),
            "total_vendas": float(round(info["total_vendas"], 2)),
            "produto_mais_vendido": produto_mais_vendido,
        }

    total_geral = float(
        round(sum(dados["total_vendas"] for dados in regioes.values()), 2)
    )

    resultado = {
        "regioes": regioes,
        "total_geral": total_geral,
        "linhas_invalidas": int(linhas_invalidas),
    }

    saida_path.parent.mkdir(parents=True, exist_ok=True)
    with open(saida_path, mode="w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    return resultado
