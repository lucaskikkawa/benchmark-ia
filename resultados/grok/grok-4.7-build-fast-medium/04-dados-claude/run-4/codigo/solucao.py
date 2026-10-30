import csv
import json
import math
from pathlib import Path

COLUNAS_OBRIGATORIAS = (
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
    resumo = _agregar(entrada_path)
    saida_path.parent.mkdir(parents=True, exist_ok=True)
    with saida_path.open("w", encoding="utf-8") as arquivo:
        json.dump(resumo, arquivo, ensure_ascii=False, indent=2)
    return resumo


def _linha_vazia(row: list[str]) -> bool:
    return len(row) == 0 or (len(row) == 1 and row[0].strip() == "")


def _agregar(entrada: Path) -> dict:
    with entrada.open(encoding="utf-8-sig", newline="") as arquivo:
        reader = csv.reader(arquivo)
        header = None
        linhas = []
        for row in reader:
            if header is None:
                if _linha_vazia(row):
                    continue
                header = row
                continue
            linhas.append(row)

    if header is None:
        raise ValueError("CSV sem cabeçalho com as colunas obrigatórias")

    nomes = [coluna.strip() for coluna in header]
    indices: dict[str, int] = {}
    for i, nome in enumerate(nomes):
        indices.setdefault(nome, i)

    faltando = [coluna for coluna in COLUNAS_OBRIGATORIAS if coluna not in indices]
    if faltando:
        raise ValueError(
            "Colunas obrigatórias ausentes: " + ", ".join(faltando)
        )

    n_colunas = len(header)
    idx_regiao = indices["regiao"]
    idx_produto = indices["produto"]
    idx_quantidade = indices["quantidade"]
    idx_preco = indices["preco_unitario"]
    idx_status = indices["status"]

    quantidade_total: dict[str, int] = {}
    total_bruto: dict[str, float] = {}
    quantidade_produto: dict[str, dict[str, int]] = {}
    linhas_invalidas = 0

    for row in linhas:
        if _linha_vazia(row):
            continue
        if len(row) != n_colunas:
            linhas_invalidas += 1
            continue

        regiao = row[idx_regiao].strip()
        produto = row[idx_produto].strip()
        quantidade_txt = row[idx_quantidade].strip()
        preco_txt = row[idx_preco].strip()
        status = row[idx_status].strip()

        if regiao == "" or produto == "":
            linhas_invalidas += 1
            continue

        try:
            quantidade = int(quantidade_txt)
        except ValueError:
            linhas_invalidas += 1
            continue
        if quantidade <= 0:
            linhas_invalidas += 1
            continue

        try:
            preco = float(preco_txt)
        except ValueError:
            linhas_invalidas += 1
            continue
        if not math.isfinite(preco) or preco < 0:
            linhas_invalidas += 1
            continue

        if status.lower() != "concluida":
            continue

        quantidade_total[regiao] = quantidade_total.get(regiao, 0) + quantidade
        total_bruto[regiao] = total_bruto.get(regiao, 0.0) + quantidade * preco
        por_produto = quantidade_produto.setdefault(regiao, {})
        por_produto[produto] = por_produto.get(produto, 0) + quantidade

    regioes: dict[str, dict] = {}
    for regiao in sorted(quantidade_total):
        por_produto = quantidade_produto[regiao]
        produto_mais_vendido = min(por_produto.items(), key=lambda item: (-item[1], item[0]))[0]
        regioes[regiao] = {
            "quantidade_total": int(quantidade_total[regiao]),
            "total_vendas": float(round(total_bruto[regiao], 2)),
            "produto_mais_vendido": produto_mais_vendido,
        }

    total_geral = float(round(sum(info["total_vendas"] for info in regioes.values()), 2))
    return {
        "regioes": regioes,
        "total_geral": total_geral,
        "linhas_invalidas": int(linhas_invalidas),
    }
