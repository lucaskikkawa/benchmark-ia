import csv
import json
import math
import os
import tempfile
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
    """Resume as vendas válidas de um CSV e grava o resultado em JSON."""
    acumulado = {}
    linhas_invalidas = 0

    # utf-8-sig aceita tanto UTF-8 comum quanto arquivos com BOM.
    with open(entrada, "r", encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.reader(arquivo)
        try:
            cabecalho = next(leitor)
        except StopIteration:
            raise ValueError("O CSV não contém cabeçalho") from None

        indices = {nome.strip(): i for i, nome in enumerate(cabecalho)}
        faltantes = [nome for nome in _COLUNAS_OBRIGATORIAS if nome not in indices]
        if faltantes:
            raise ValueError(f"Colunas obrigatórias ausentes: {', '.join(faltantes)}")

        for linha in leitor:
            valores = [valor.strip() for valor in linha]
            if not valores or all(valor == "" for valor in valores):
                continue

            if len(valores) != len(cabecalho):
                linhas_invalidas += 1
                continue

            regiao = valores[indices["regiao"]]
            produto = valores[indices["produto"]]
            quantidade_txt = valores[indices["quantidade"]]
            preco_txt = valores[indices["preco_unitario"]]
            status = valores[indices["status"]]

            try:
                quantidade = int(quantidade_txt)
                preco = float(preco_txt)
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

            if status.lower() != "concluida":
                continue

            regiao_dados = acumulado.setdefault(
                regiao, {"quantidade_total": 0, "total_vendas": 0.0, "produtos": {}}
            )
            regiao_dados["quantidade_total"] += quantidade
            regiao_dados["total_vendas"] += quantidade * preco
            regiao_dados["produtos"][produto] = (
                regiao_dados["produtos"].get(produto, 0) + quantidade
            )

    regioes = {}
    for regiao in sorted(acumulado):
        dados = acumulado[regiao]
        produto_mais_vendido = min(
            dados["produtos"], key=lambda produto: (-dados["produtos"][produto], produto)
        )
        regioes[regiao] = {
            "quantidade_total": dados["quantidade_total"],
            "total_vendas": float(round(dados["total_vendas"], 2)),
            "produto_mais_vendido": produto_mais_vendido,
        }

    resumo = {
        "regioes": regioes,
        "total_geral": float(round(sum(r["total_vendas"] for r in regioes.values()), 2)),
        "linhas_invalidas": linhas_invalidas,
    }

    # Serializa antes de criar/tocar a saída; substitui atomicamente ao concluir.
    conteudo = json.dumps(resumo, ensure_ascii=False, indent=2)
    destino = Path(saida)
    destino.parent.mkdir(parents=True, exist_ok=True)
    temporario = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=destino.parent, delete=False
        ) as arquivo_temp:
            temporario = arquivo_temp.name
            arquivo_temp.write(conteudo)
            arquivo_temp.write("\n")
        os.replace(temporario, destino)
        temporario = None
    finally:
        if temporario is not None:
            try:
                os.unlink(temporario)
            except FileNotFoundError:
                pass

    return resumo
