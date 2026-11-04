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
    caminho_entrada = Path(entrada)
    caminho_saida = Path(saida)
    resumo = _calcular_resumo(caminho_entrada)
    _escrever_json(caminho_saida, resumo)
    return resumo


def _calcular_resumo(caminho: Path) -> dict:
    with caminho.open(encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.reader(arquivo)
        cabecalho, indices = _ler_cabecalho(leitor)
        return _agregar(leitor, indices, len(cabecalho))


def _ler_cabecalho(leitor) -> tuple[list[str], dict[str, int]]:
    for campos in leitor:
        if _linha_em_branco(campos):
            continue
        cabecalho = [campo.strip() for campo in campos]
        indices: dict[str, int] = {}
        for indice, nome in enumerate(cabecalho):
            indices.setdefault(nome, indice)
        ausentes = [nome for nome in COLUNAS_OBRIGATORIAS if nome not in indices]
        if ausentes:
            raise ValueError(
                "Colunas obrigatórias ausentes: " + ", ".join(ausentes)
            )
        return cabecalho, indices
    raise ValueError("CSV sem cabeçalho")


def _linha_em_branco(campos: list[str]) -> bool:
    if not campos:
        return True
    return len(campos) == 1 and campos[0].strip() == ""


def _agregar(leitor, indices: dict[str, int], n_campos: int) -> dict:
    grupos: dict[str, dict] = {}
    invalidas = 0
    for campos in leitor:
        if _linha_em_branco(campos):
            continue
        venda = _interpretar(campos, indices, n_campos)
        if venda is None:
            invalidas += 1
            continue
        regiao, produto, quantidade, preco, status = venda
        if status.lower() != "concluida":
            continue
        _acumular(grupos, regiao, produto, quantidade, preco)
    return _montar_resumo(grupos, invalidas)


def _interpretar(campos: list[str], indices: dict[str, int], n_campos: int):
    if len(campos) != n_campos:
        return None
    valores = [campo.strip() for campo in campos]
    regiao = valores[indices["regiao"]]
    produto = valores[indices["produto"]]
    if regiao == "" or produto == "":
        return None
    quantidade = _para_quantidade(valores[indices["quantidade"]])
    if quantidade is None:
        return None
    preco = _para_preco(valores[indices["preco_unitario"]])
    if preco is None:
        return None
    return regiao, produto, quantidade, preco, valores[indices["status"]]


def _para_quantidade(valor: str) -> int | None:
    try:
        quantidade = int(valor)
    except ValueError:
        return None
    if quantidade <= 0:
        return None
    return quantidade


def _para_preco(valor: str) -> float | None:
    try:
        preco = float(valor)
    except ValueError:
        return None
    if not math.isfinite(preco) or preco < 0:
        return None
    return preco


def _acumular(
    grupos: dict[str, dict],
    regiao: str,
    produto: str,
    quantidade: int,
    preco: float,
) -> None:
    grupo = grupos.get(regiao)
    if grupo is None:
        grupo = {"quantidade_total": 0, "total": 0.0, "produtos": {}}
        grupos[regiao] = grupo
    grupo["quantidade_total"] += quantidade
    grupo["total"] += quantidade * preco
    produtos = grupo["produtos"]
    produtos[produto] = produtos.get(produto, 0) + quantidade


def _produto_mais_vendido(produtos: dict[str, int]) -> str:
    return min(produtos, key=lambda nome: (-produtos[nome], nome))


def _arredondar(valor: float) -> float:
    arredondado = float(round(valor, 2))
    if arredondado == 0:
        return 0.0
    return arredondado


def _montar_resumo(grupos: dict[str, dict], invalidas: int) -> dict:
    regioes = {}
    for nome in sorted(grupos):
        grupo = grupos[nome]
        regioes[nome] = {
            "quantidade_total": int(grupo["quantidade_total"]),
            "total_vendas": _arredondar(grupo["total"]),
            "produto_mais_vendido": _produto_mais_vendido(grupo["produtos"]),
        }
    total_geral = _arredondar(
        sum((item["total_vendas"] for item in regioes.values()), 0.0)
    )
    return {
        "regioes": regioes,
        "total_geral": total_geral,
        "linhas_invalidas": int(invalidas),
    }


def _escrever_json(caminho: Path, resumo: dict) -> None:
    texto = json.dumps(resumo, ensure_ascii=False, indent=2)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(texto, encoding="utf-8", newline="\n")
