"""Agrega um CSV de vendas e grava o resumo em JSON."""

import csv
import json
import math
from pathlib import Path

_COLUNAS = (
    "data",
    "regiao",
    "produto",
    "quantidade",
    "preco_unitario",
    "status",
)


def resumir_vendas(entrada: str | Path, saida: str | Path) -> dict:
    """Lê o CSV em `entrada`, grava o resumo JSON em `saida` e o retorna.

    Em caso de arquivo ausente ou de cabeçalho inválido, `saida` não é
    criado nem alterado.
    """
    resumo = _agregar(Path(entrada))
    _escrever(Path(saida), resumo)
    return resumo


def _agregar(entrada: Path) -> dict:
    with entrada.open(encoding="utf-8-sig", newline="") as arquivo:
        linhas = list(csv.reader(arquivo))

    inicio = 0
    while inicio < len(linhas) and _linha_vazia(linhas[inicio]):
        inicio += 1
    if inicio == len(linhas):
        raise ValueError("CSV sem cabeçalho com as colunas obrigatórias")

    cabecalho = linhas[inicio]
    indice: dict[str, int] = {}
    for posicao, nome in enumerate(cabecalho):
        indice.setdefault(nome.strip(), posicao)

    ausentes = [coluna for coluna in _COLUNAS if coluna not in indice]
    if ausentes:
        raise ValueError("Colunas obrigatórias ausentes: " + ", ".join(ausentes))

    n_campos = len(cabecalho)
    agregados: dict[str, dict] = {}
    invalidas = 0

    for linha in linhas[inicio + 1 :]:
        if _linha_vazia(linha):
            continue
        registro = _registro_valido(linha, n_campos, indice)
        if registro is None:
            invalidas += 1
            continue
        regiao, produto, quantidade, preco, status = registro
        if status.lower() != "concluida":
            continue

        grupo = agregados.get(regiao)
        if grupo is None:
            grupo = {"quantidade_total": 0, "total": 0.0, "produtos": {}}
            agregados[regiao] = grupo
        grupo["quantidade_total"] += quantidade
        grupo["total"] += quantidade * preco
        produtos: dict[str, int] = grupo["produtos"]
        produtos[produto] = produtos.get(produto, 0) + quantidade

    regioes: dict[str, dict] = {}
    for regiao in sorted(agregados):
        grupo = agregados[regiao]
        produtos = grupo["produtos"]
        maior_qtd = max(produtos.values())
        produto_top = min(nome for nome, qtd in produtos.items() if qtd == maior_qtd)
        regioes[regiao] = {
            "quantidade_total": grupo["quantidade_total"],
            "total_vendas": _moeda(grupo["total"]),
            "produto_mais_vendido": produto_top,
        }

    return {
        "regioes": regioes,
        "total_geral": _moeda(sum(item["total_vendas"] for item in regioes.values())),
        "linhas_invalidas": invalidas,
    }


def _linha_vazia(campos: list[str]) -> bool:
    # Linha em branco ou só com espaços, sem separador. Uma linha como
    # ",,,," tem campos vazios e segue para a validação.
    if not campos:
        return True
    return len(campos) == 1 and campos[0].strip() == ""


def _registro_valido(
    linha: list[str], n_campos: int, indice: dict[str, int]
) -> tuple[str, str, int, float, str] | None:
    if len(linha) != n_campos:
        return None

    regiao = linha[indice["regiao"]].strip()
    produto = linha[indice["produto"]].strip()
    if regiao == "" or produto == "":
        return None

    try:
        quantidade = int(linha[indice["quantidade"]].strip())
    except ValueError:
        return None
    if quantidade <= 0:
        return None

    try:
        preco = float(linha[indice["preco_unitario"]].strip())
    except ValueError:
        return None
    if not math.isfinite(preco) or preco < 0:
        return None

    status = linha[indice["status"]].strip()
    return regiao, produto, quantidade, preco, status


def _moeda(valor: float) -> float:
    arredondado = float(round(float(valor), 2))
    # json.dumps(-0.0) emite "-0.0"; o zero monetário fica não negativo.
    if arredondado == 0:
        return 0.0
    return arredondado


def _escrever(saida: Path, resumo: dict) -> None:
    saida.parent.mkdir(parents=True, exist_ok=True)
    with saida.open("w", encoding="utf-8", newline="\n") as arquivo:
        json.dump(resumo, arquivo, ensure_ascii=False, indent=2)
