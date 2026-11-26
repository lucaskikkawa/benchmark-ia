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

    regioes_totais: dict[str, dict[str, object]] = {}
    linhas_invalidas = 0

    with entrada_path.open("r", encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.reader(arquivo, delimiter=",", quotechar='"')
        cabecalho = next(leitor, None)
        if cabecalho is None:
            raise ValueError("Arquivo CSV vazio: cabeçalho ausente.")

        indices: dict[str, int] = {}
        for idx, nome in enumerate(cabecalho):
            nome_limpo = nome.strip()
            if nome_limpo not in indices:
                indices[nome_limpo] = idx

        faltantes = [col for col in COLUNAS_OBRIGATORIAS if col not in indices]
        if faltantes:
            raise ValueError(
                f"Colunas obrigatórias ausentes no cabeçalho: {', '.join(faltantes)}"
            )

        num_colunas = len(cabecalho)
        idx_regiao = indices["regiao"]
        idx_produto = indices["produto"]
        idx_quantidade = indices["quantidade"]
        idx_preco = indices["preco_unitario"]
        idx_status = indices["status"]

        for linha in leitor:
            campos = [valor.strip() for valor in linha]
            if not any(campos):
                continue

            if len(campos) != num_colunas:
                linhas_invalidas += 1
                continue

            regiao = campos[idx_regiao]
            produto = campos[idx_produto]
            if not regiao or not produto:
                linhas_invalidas += 1
                continue

            try:
                quantidade = int(campos[idx_quantidade])
            except ValueError:
                linhas_invalidas += 1
                continue

            if quantidade <= 0:
                linhas_invalidas += 1
                continue

            try:
                preco_unitario = float(campos[idx_preco])
            except ValueError:
                linhas_invalidas += 1
                continue

            if not math.isfinite(preco_unitario) or preco_unitario < 0:
                linhas_invalidas += 1
                continue

            status = campos[idx_status]
            if status.lower() != "concluida":
                continue

            dados_regiao = regioes_totais.get(regiao)
            if dados_regiao is None:
                dados_regiao = {
                    "quantidade_total": 0,
                    "total_vendas": 0.0,
                    "produtos": defaultdict(int),
                }
                regioes_totais[regiao] = dados_regiao

            dados_regiao["quantidade_total"] += quantidade
            dados_regiao["total_vendas"] += quantidade * preco_unitario
            dados_regiao["produtos"][produto] += quantidade

    regioes_resultado: dict[str, dict[str, int | float | str]] = {}
    for regiao in sorted(regioes_totais):
        dados = regioes_totais[regiao]
        produtos: dict[str, int] = dados["produtos"]
        produto_mais_vendido = min(
            produtos.items(), key=lambda item: (-item[1], item[0])
        )[0]
        total_vendas = float(round(dados["total_vendas"], 2)) + 0.0
        regioes_resultado[regiao] = {
            "quantidade_total": int(dados["quantidade_total"]),
            "total_vendas": total_vendas,
            "produto_mais_vendido": produto_mais_vendido,
        }

    total_geral = (
        float(
            round(
                sum((info["total_vendas"] for info in regioes_resultado.values()), 0.0),
                2,
            )
        )
        + 0.0
    )

    resultado = {
        "regioes": regioes_resultado,
        "total_geral": total_geral,
        "linhas_invalidas": int(linhas_invalidas),
    }

    saida_path = Path(saida)
    saida_path.parent.mkdir(parents=True, exist_ok=True)
    with saida_path.open("w", encoding="utf-8") as arquivo_saida:
        json.dump(resultado, arquivo_saida, ensure_ascii=False, indent=2)

    return resultado
