import csv
import json
import math
import os
import tempfile
from collections import defaultdict
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
    """Resume as vendas válidas de um CSV e grava o resultado como JSON."""
    acumulado = {}
    linhas_invalidas = 0

    with Path(entrada).open("r", encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.reader(arquivo)
        try:
            cabecalho = next(leitor)
        except StopIteration:
            cabecalho = []

        cabecalho = [nome.strip() for nome in cabecalho]
        indices = {nome: indice for indice, nome in enumerate(cabecalho)}
        faltantes = [nome for nome in COLUNAS_OBRIGATORIAS if nome not in indices]
        if faltantes:
            raise ValueError(
                "Colunas obrigatórias ausentes: " + ", ".join(faltantes)
            )

        for linha in leitor:
            # csv.reader representa uma linha física vazia como uma lista vazia.
            if not linha:
                continue

            valores = [valor.strip() for valor in linha]
            if len(valores) != len(cabecalho):
                linhas_invalidas += 1
                continue

            regiao = valores[indices["regiao"]]
            produto = valores[indices["produto"]]
            try:
                quantidade = int(valores[indices["quantidade"]])
                preco = float(valores[indices["preco_unitario"]])
            except ValueError:
                linhas_invalidas += 1
                continue

            if (
                not regiao
                or not produto
                or quantidade <= 0
                or not math.isfinite(preco)
                or preco < 0
            ):
                linhas_invalidas += 1
                continue

            if valores[indices["status"]].lower() != "concluida":
                continue

            dados_regiao = acumulado.setdefault(
                regiao, {"quantidade_total": 0, "valor": 0.0, "produtos": defaultdict(int)}
            )
            dados_regiao["quantidade_total"] += quantidade
            dados_regiao["valor"] += quantidade * preco
            dados_regiao["produtos"][produto] += quantidade

    regioes = {}
    for regiao in sorted(acumulado):
        dados = acumulado[regiao]
        maior_quantidade = max(dados["produtos"].values())
        produto_mais_vendido = min(
            produto
            for produto, quantidade in dados["produtos"].items()
            if quantidade == maior_quantidade
        )
        regioes[regiao] = {
            "quantidade_total": dados["quantidade_total"],
            "total_vendas": round(dados["valor"], 2),
            "produto_mais_vendido": produto_mais_vendido,
        }

    resumo = {
        "regioes": regioes,
        "total_geral": round(sum(item["total_vendas"] for item in regioes.values()), 2),
        "linhas_invalidas": linhas_invalidas,
    }

    caminho_saida = Path(saida)
    caminho_saida.parent.mkdir(parents=True, exist_ok=True)
    temporario = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="",
            dir=caminho_saida.parent,
            delete=False,
        ) as arquivo_saida:
            temporario = arquivo_saida.name
            json.dump(resumo, arquivo_saida, ensure_ascii=False, indent=2, allow_nan=False)
            arquivo_saida.write("\n")
        os.replace(temporario, caminho_saida)
        temporario = None
    finally:
        if temporario is not None:
            try:
                os.unlink(temporario)
            except FileNotFoundError:
                pass

    return resumo
