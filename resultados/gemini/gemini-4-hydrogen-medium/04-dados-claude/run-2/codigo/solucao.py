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
    stripped: list[str], col_idx: dict[str, int]
) -> tuple[str, str, int, float, str] | None:
    regiao = stripped[col_idx["regiao"]]
    produto = stripped[col_idx["produto"]]
    if not regiao or not produto:
        return None

    try:
        quantidade = int(stripped[col_idx["quantidade"]])
    except ValueError:
        return None
    if quantidade <= 0:
        return None

    try:
        preco = float(stripped[col_idx["preco_unitario"]])
    except ValueError:
        return None
    if not math.isfinite(preco) or preco < 0:
        return None

    status = stripped[col_idx["status"]]
    return regiao, produto, quantidade, preco, status


def resumir_vendas(entrada: str | Path, saida: str | Path) -> dict:
    entrada_path = Path(entrada)
    saida_path = Path(saida)

    linhas_invalidas = 0
    regiao_qtd: dict[str, int] = defaultdict(int)
    regiao_total: dict[str, float] = defaultdict(float)
    regiao_produtos: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    with entrada_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        try:
            raw_header = next(reader)
        except StopIteration as exc:
            raise ValueError("Arquivo CSV vazio: cabeçalho ausente.") from exc

        header = [col.strip() for col in raw_header]
        num_cols = len(header)
        col_idx: dict[str, int] = {}
        for idx, name in enumerate(header):
            if name not in col_idx:
                col_idx[name] = idx

        missing = [col for col in REQUIRED_COLUMNS if col not in col_idx]
        if missing:
            raise ValueError(f"Colunas obrigatórias ausentes: {', '.join(missing)}")

        for row in reader:
            if not row:
                continue
            stripped = [val.strip() for val in row]
            if all(val == "" for val in stripped):
                continue

            if len(stripped) != num_cols:
                linhas_invalidas += 1
                continue

            parsed = _parse_valid_row(stripped, col_idx)
            if parsed is None:
                linhas_invalidas += 1
                continue

            regiao, produto, quantidade, preco, status = parsed
            if status.lower() != "concluida":
                continue

            regiao_qtd[regiao] += quantidade
            regiao_total[regiao] += quantidade * preco
            regiao_produtos[regiao][produto] += quantidade

    regioes: dict[str, dict] = {}
    for regiao in sorted(regiao_qtd):
        produtos = regiao_produtos[regiao]
        produto_mais_vendido = min(produtos, key=lambda p: (-produtos[p], p))
        regioes[regiao] = {
            "quantidade_total": int(regiao_qtd[regiao]),
            "total_vendas": float(round(regiao_total[regiao], 2)),
            "produto_mais_vendido": produto_mais_vendido,
        }

    total_geral = float(round(sum(r["total_vendas"] for r in regioes.values()), 2))
    resultado = {
        "regioes": regioes,
        "total_geral": total_geral,
        "linhas_invalidas": int(linhas_invalidas),
    }

    saida_path.parent.mkdir(parents=True, exist_ok=True)
    with saida_path.open("w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    return resultado
