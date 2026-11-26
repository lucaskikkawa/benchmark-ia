from collections import defaultdict
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

    linhas_invalidas = 0
    qtd_por_regiao: dict[str, int] = defaultdict(int)
    vendas_por_regiao: dict[str, float] = defaultdict(float)
    qtd_por_regiao_produto: dict[str, dict[str, int]] = defaultdict(
        lambda: defaultdict(int)
    )

    with entrada_path.open("r", encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.reader(arquivo)
        cabecalho = next(leitor, None)
        if cabecalho is None:
            raise ValueError("Arquivo CSV vazio: cabeçalho ausente.")

        colunas = [coluna.strip() for coluna in cabecalho]
        num_colunas = len(colunas)
        indices = {nome: i for i, nome in enumerate(colunas)}

        faltantes = [col for col in COLUNAS_OBRIGATORIAS if col not in indices]
        if faltantes:
            raise ValueError(
                f"Colunas obrigatórias ausentes no cabeçalho: {', '.join(faltantes)}"
            )

        idx_regiao = indices["regiao"]
        idx_produto = indices["produto"]
        idx_quantidade = indices["quantidade"]
        idx_preco = indices["preco_unitario"]
        idx_status = indices["status"]

        for linha in leitor:
            if not linha or (len(linha) == 1 and not linha[0].strip()):
                continue

            valores = [valor.strip() for valor in linha]
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

            qtd_por_regiao[regiao] += quantidade
            vendas_por_regiao[regiao] += quantidade * preco_unitario
            qtd_por_regiao_produto[regiao][produto] += quantidade

    regioes: dict[str, dict] = {}
    for regiao in sorted(qtd_por_regiao):
        total_vendas = float(round(vendas_por_regiao[regiao], 2)) + 0.0
        produto_mais_vendido = min(
            qtd_por_regiao_produto[regiao].items(),
            key=lambda item: (-item[1], item[0]),
        )[0]
        regioes[regiao] = {
            "quantidade_total": int(qtd_por_regiao[regiao]),
            "total_vendas": total_vendas,
            "produto_mais_vendido": produto_mais_vendido,
        }

    total_geral = (
        float(round(sum(info["total_vendas"] for info in regioes.values()), 2)) + 0.0
    )

    resumo = {
        "regioes": regioes,
        "total_geral": total_geral,
        "linhas_invalidas": int(linhas_invalidas),
    }

    saida_path.parent.mkdir(parents=True, exist_ok=True)
    with saida_path.open("w", encoding="utf-8") as arquivo_saida:
        json.dump(resumo, arquivo_saida, ensure_ascii=False, indent=2)

    return resumo
