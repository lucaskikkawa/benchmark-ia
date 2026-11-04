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
    """Resume as vendas concluídas de um CSV e grava o resultado em JSON."""
    regioes = {}
    linhas_invalidas = 0

    # O modo newline="" deixa a biblioteca csv tratar corretamente campos
    # entre aspas que contenham quebras de linha.
    with Path(entrada).open("r", encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.reader(arquivo)
        try:
            cabecalho = next(leitor)
        except StopIteration:
            raise ValueError("O CSV não contém cabeçalho") from None

        cabecalho = [nome.strip() for nome in cabecalho]
        indices = {}
        for coluna in COLUNAS_OBRIGATORIAS:
            try:
                indices[coluna] = cabecalho.index(coluna)
            except ValueError:
                raise ValueError(f"Coluna obrigatória ausente: {coluna}") from None

        for linha in leitor:
            valores = [valor.strip() for valor in linha]
            if not valores or all(valor == "" for valor in valores):
                continue

            if len(valores) != len(cabecalho):
                linhas_invalidas += 1
                continue

            regiao = valores[indices["regiao"]]
            produto = valores[indices["produto"]]
            try:
                quantidade = int(valores[indices["quantidade"]])
                preco_unitario = float(valores[indices["preco_unitario"]])
            except ValueError:
                linhas_invalidas += 1
                continue

            if (
                not regiao
                or not produto
                or quantidade <= 0
                or not math.isfinite(preco_unitario)
                or preco_unitario < 0
            ):
                linhas_invalidas += 1
                continue

            if valores[indices["status"]].lower() != "concluida":
                continue

            dados_regiao = regioes.setdefault(
                regiao,
                {"quantidade_total": 0, "valor_bruto": 0.0, "produtos": {}},
            )
            dados_regiao["quantidade_total"] += quantidade
            dados_regiao["valor_bruto"] += quantidade * preco_unitario
            dados_regiao["produtos"][produto] = (
                dados_regiao["produtos"].get(produto, 0) + quantidade
            )

    regioes_saida = {}
    for regiao in sorted(regioes):
        dados = regioes[regiao]
        produto_mais_vendido = min(
            dados["produtos"],
            key=lambda produto: (-dados["produtos"][produto], produto),
        )
        regioes_saida[regiao] = {
            "quantidade_total": dados["quantidade_total"],
            "total_vendas": round(dados["valor_bruto"], 2),
            "produto_mais_vendido": produto_mais_vendido,
        }

    resumo = {
        "regioes": regioes_saida,
        "total_geral": round(
            sum(regiao["total_vendas"] for regiao in regioes_saida.values()), 2
        ),
        "linhas_invalidas": linhas_invalidas,
    }

    caminho_saida = Path(saida)
    caminho_saida.parent.mkdir(parents=True, exist_ok=True)
    with caminho_saida.open("w", encoding="utf-8", newline="") as arquivo:
        json.dump(resumo, arquivo, ensure_ascii=False, indent=2)

    return resumo
