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
    """Lê, agrega e grava o resumo de um CSV de vendas."""
    entrada = Path(entrada)
    saida = Path(saida)

    agregados = {}
    linhas_invalidas = 0

    # utf-8-sig aceita tanto UTF-8 comum quanto arquivos iniciados por BOM.
    with entrada.open("r", encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.reader(arquivo)
        try:
            cabecalho = next(leitor)
        except StopIteration:
            raise ValueError("O CSV não contém cabeçalho") from None

        cabecalho = [nome.strip() for nome in cabecalho]
        indices = {}
        for coluna in _COLUNAS_OBRIGATORIAS:
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
                valido = (
                    bool(regiao)
                    and bool(produto)
                    and quantidade > 0
                    and math.isfinite(preco_unitario)
                    and preco_unitario >= 0
                )
            except (ValueError, OverflowError):
                valido = False

            if not valido:
                linhas_invalidas += 1
                continue

            if valores[indices["status"]].lower() != "concluida":
                continue

            regiao_info = agregados.setdefault(
                regiao, {"quantidade_total": 0, "vendas": 0.0, "produtos": {}}
            )
            regiao_info["quantidade_total"] += quantidade
            regiao_info["vendas"] += quantidade * preco_unitario
            regiao_info["produtos"][produto] = (
                regiao_info["produtos"].get(produto, 0) + quantidade
            )

    regioes = {}
    for regiao in sorted(agregados):
        dados = agregados[regiao]
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
        "total_geral": round(
            sum(dados["total_vendas"] for dados in regioes.values()), 2
        ),
        "linhas_invalidas": linhas_invalidas,
    }

    # Só toca no destino depois de ler e processar a entrada sem erros.
    saida.parent.mkdir(parents=True, exist_ok=True)
    temporario = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="",
            dir=saida.parent,
            prefix=f".{saida.name}.",
            suffix=".tmp",
            delete=False,
        ) as arquivo_saida:
            temporario = Path(arquivo_saida.name)
            json.dump(resumo, arquivo_saida, ensure_ascii=False, indent=2)
            arquivo_saida.write("\n")
        os.replace(temporario, saida)
    finally:
        if temporario is not None:
            temporario.unlink(missing_ok=True)

    return resumo
