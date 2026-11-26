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
    """Lê um CSV de vendas, agrega por região, escreve JSON em `saida` e retorna o resumo."""
    entrada_path = Path(entrada)
    saida_path = Path(saida)

    regioes_qtd: dict[str, int] = defaultdict(int)
    regioes_total: dict[str, float] = defaultdict(float)
    regioes_produtos: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    linhas_invalidas = 0

    with entrada_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f, delimiter=",", quotechar='"')
        header = next(reader, None)
        if header is None:
            raise ValueError("Arquivo CSV vazio: cabeçalho ausente.")

        header_norm = [col.strip() for col in header]
        col_index: dict[str, int] = {}
        for idx, name in enumerate(header_norm):
            if name not in col_index:
                col_index[name] = idx

        missing = [col for col in REQUIRED_COLUMNS if col not in col_index]
        if missing:
            raise ValueError(f"Colunas obrigatórias ausentes: {', '.join(missing)}")

        idx_regiao = col_index["regiao"]
        idx_produto = col_index["produto"]
        idx_quantidade = col_index["quantidade"]
        idx_preco = col_index["preco_unitario"]
        idx_status = col_index["status"]
        num_cols = len(header)

        for row in reader:
            if not row:
                continue

            if len(row) != num_cols:
                linhas_invalidas += 1
                continue

            regiao = row[idx_regiao].strip()
            produto = row[idx_produto].strip()
            qtd_str = row[idx_quantidade].strip()
            preco_str = row[idx_preco].strip()
            status = row[idx_status].strip()

            if not regiao or not produto:
                linhas_invalidas += 1
                continue

            try:
                quantidade = int(qtd_str)
                preco = float(preco_str)
            except ValueError:
                linhas_invalidas += 1
                continue

            if quantidade <= 0 or not math.isfinite(preco) or preco < 0:
                linhas_invalidas += 1
                continue

            if status.lower() != "concluida":
                continue

            regioes_qtd[regiao] += quantidade
            regioes_total[regiao] += quantidade * preco
            regioes_produtos[regiao][produto] += quantidade

    regioes: dict[str, dict[str, int | float | str]] = {}
    for regiao in sorted(regioes_qtd):
        produto_mais_vendido = min(
            regioes_produtos[regiao].items(),
            key=lambda item: (-item[1], item[0]),
        )[0]
        total_vendas = float(round(regioes_total[regiao], 2)) + 0.0
        regioes[regiao] = {
            "quantidade_total": regioes_qtd[regiao],
            "total_vendas": total_vendas,
            "produto_mais_vendido": produto_mais_vendido,
        }

    total_geral = float(round(sum(r["total_vendas"] for r in regioes.values()), 2)) + 0.0

    resultado = {
        "regioes": regioes,
        "total_geral": total_geral,
        "linhas_invalidas": linhas_invalidas,
    }

    saida_path.parent.mkdir(parents=True, exist_ok=True)
    with saida_path.open("w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    return resultado
