import csv
import json
import math
import os
import tempfile
from collections import defaultdict
from pathlib import Path


def resumir_vendas(entrada: str | Path, saida: str | Path) -> dict:
    """Resume as vendas válidas de um CSV e grava o resultado em JSON."""
    caminho_entrada = Path(entrada)

    with caminho_entrada.open("r", encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.reader(arquivo)
        try:
            cabecalho = next(leitor)
        except StopIteration:
            raise ValueError("O CSV não contém cabeçalho") from None

        nomes = [nome.strip() for nome in cabecalho]
        indices = {nome: indice for indice, nome in enumerate(nomes)}
        obrigatorias = (
            "data",
            "regiao",
            "produto",
            "quantidade",
            "preco_unitario",
            "status",
        )
        faltantes = [nome for nome in obrigatorias if nome not in indices]
        if faltantes:
            raise ValueError(
                "Colunas obrigatórias ausentes: " + ", ".join(faltantes)
            )

        agregados = {}
        linhas_invalidas = 0

        for linha in leitor:
            valores = [valor.strip() for valor in linha]
            if not valores or all(valor == "" for valor in valores):
                continue

            if len(valores) != len(nomes):
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

            status = valores[indices["status"]]
            if status.casefold() != "concluida":
                continue

            if regiao not in agregados:
                agregados[regiao] = {
                    "quantidade_total": 0,
                    "valor": 0.0,
                    "produtos": defaultdict(int),
                }
            dados = agregados[regiao]
            dados["quantidade_total"] += quantidade
            dados["valor"] += quantidade * preco
            dados["produtos"][produto] += quantidade

    regioes = {}
    for regiao in sorted(agregados):
        dados = agregados[regiao]
        mais_vendido = min(
            dados["produtos"],
            key=lambda produto: (-dados["produtos"][produto], produto),
        )
        regioes[regiao] = {
            "quantidade_total": dados["quantidade_total"],
            "total_vendas": round(dados["valor"], 2),
            "produto_mais_vendido": mais_vendido,
        }

    resumo = {
        "regioes": regioes,
        "total_geral": round(
            sum(dados["total_vendas"] for dados in regioes.values()), 2
        ),
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
            prefix=f".{caminho_saida.name}.",
            suffix=".tmp",
            delete=False,
        ) as arquivo_saida:
            temporario = arquivo_saida.name
            json.dump(resumo, arquivo_saida, ensure_ascii=False, indent=2)
            arquivo_saida.write("\n")
        os.replace(temporario, caminho_saida)
    finally:
        if temporario is not None and os.path.exists(temporario):
            os.unlink(temporario)

    return resumo
