import csv
import json
import math
from pathlib import Path


def resumir_vendas(entrada: str | Path, saida: str | Path) -> dict:
    """Lê um CSV de vendas, resume as vendas concluídas e grava o resultado em JSON."""
    entrada = Path(entrada)

    obrigatorias = (
        "data",
        "regiao",
        "produto",
        "quantidade",
        "preco_unitario",
        "status",
    )

    agregados = {}
    linhas_invalidas = 0

    # Todo o processamento de entrada acontece antes de abrir a saída, para que
    # erros de leitura ou de cabeçalho não criem nem alterem o arquivo de saída.
    with entrada.open("r", encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.reader(arquivo)
        cabecalho = next(leitor, None)
        if cabecalho is None:
            raise ValueError("O CSV não contém cabeçalho")

        cabecalho = [nome.strip() for nome in cabecalho]
        indices = {}
        for nome in obrigatorias:
            if nome not in cabecalho:
                raise ValueError(f"Coluna obrigatória ausente: {nome}")
            indices[nome] = cabecalho.index(nome)

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
                preco = float(valores[indices["preco_unitario"]])
                valido = (
                    bool(regiao)
                    and bool(produto)
                    and quantidade > 0
                    and math.isfinite(preco)
                    and preco >= 0
                )
            except (ValueError, OverflowError):
                valido = False

            if not valido:
                linhas_invalidas += 1
                continue

            if valores[indices["status"]].lower() != "concluida":
                continue

            regiao_agregada = agregados.setdefault(
                regiao, {"quantidade_total": 0, "vendas": 0.0, "produtos": {}}
            )
            regiao_agregada["quantidade_total"] += quantidade
            regiao_agregada["vendas"] += quantidade * preco
            regiao_agregada["produtos"][produto] = (
                regiao_agregada["produtos"].get(produto, 0) + quantidade
            )

    regioes = {}
    for regiao in sorted(agregados):
        dados = agregados[regiao]
        maior_quantidade = max(dados["produtos"].values())
        mais_vendido = min(
            produto
            for produto, quantidade in dados["produtos"].items()
            if quantidade == maior_quantidade
        )
        regioes[regiao] = {
            "quantidade_total": dados["quantidade_total"],
            "total_vendas": float(round(dados["vendas"], 2)),
            "produto_mais_vendido": mais_vendido,
        }

    resumo = {
        "regioes": regioes,
        "total_geral": float(round(sum(r["total_vendas"] for r in regioes.values()), 2)),
        "linhas_invalidas": linhas_invalidas,
    }

    caminho_saida = Path(saida)
    caminho_saida.parent.mkdir(parents=True, exist_ok=True)
    with caminho_saida.open("w", encoding="utf-8", newline="") as arquivo:
        json.dump(resumo, arquivo, ensure_ascii=False, indent=2)
        arquivo.write("\n")

    return resumo
