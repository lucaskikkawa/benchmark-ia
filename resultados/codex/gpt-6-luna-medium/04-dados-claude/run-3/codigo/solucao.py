import csv
import json
import math
from pathlib import Path


_COLUNAS_OBRIGATORIAS = (
    "data",
    "regiao",
    "produto",
    "quantidade",
    "preco_unitario",
    "status",
)


def resumir_vendas(entrada: str | Path, saida: str | Path) -> dict:
    """Lê um CSV de vendas, resume as vendas concluídas e grava o resultado em JSON."""
    acumulado = {}
    linhas_invalidas = 0

    # Todo o processamento ocorre antes de tocar no destino: erros na leitura ou
    # no cabeçalho não criam nem alteram o arquivo de saída.
    with open(entrada, "r", encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.reader(arquivo)
        try:
            cabecalho = next(leitor)
        except StopIteration:
            raise ValueError("CSV sem cabeçalho") from None

        cabecalho = [nome.strip() for nome in cabecalho]
        faltantes = [nome for nome in _COLUNAS_OBRIGATORIAS if nome not in cabecalho]
        if faltantes:
            raise ValueError(f"Colunas obrigatórias ausentes: {', '.join(faltantes)}")

        indices = {nome: cabecalho.index(nome) for nome in _COLUNAS_OBRIGATORIAS}

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

            regiao_dados = acumulado.setdefault(
                regiao, {"quantidade_total": 0, "vendas": 0.0, "produtos": {}}
            )
            regiao_dados["quantidade_total"] += quantidade
            regiao_dados["vendas"] += quantidade * preco
            regiao_dados["produtos"][produto] = (
                regiao_dados["produtos"].get(produto, 0) + quantidade
            )

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
            "total_vendas": round(dados["vendas"], 2),
            "produto_mais_vendido": produto_mais_vendido,
        }

    resumo = {
        "regioes": regioes,
        "total_geral": round(sum(item["total_vendas"] for item in regioes.values()), 2),
        "linhas_invalidas": linhas_invalidas,
    }

    destino = Path(saida)
    destino.parent.mkdir(parents=True, exist_ok=True)
    with destino.open("w", encoding="utf-8", newline="") as arquivo:
        json.dump(resumo, arquivo, ensure_ascii=False, indent=2)
        arquivo.write("\n")

    return resumo
