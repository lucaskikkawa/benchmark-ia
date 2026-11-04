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
    entrada = Path(entrada)
    saida = Path(saida)

    with entrada.open(encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.reader(arquivo)
        try:
            cabecalho = next(leitor)
        except StopIteration:
            raise ValueError("CSV sem cabeçalho") from None

        nomes = [coluna.strip() for coluna in cabecalho]
        indices: dict[str, int] = {}
        for indice, nome in enumerate(nomes):
            indices.setdefault(nome, indice)

        ausentes = [coluna for coluna in COLUNAS_OBRIGATORIAS if coluna not in indices]
        if ausentes:
            raise ValueError(
                "Colunas obrigatórias ausentes: " + ", ".join(ausentes)
            )

        n_colunas = len(nomes)
        i_regiao = indices["regiao"]
        i_produto = indices["produto"]
        i_quantidade = indices["quantidade"]
        i_preco = indices["preco_unitario"]
        i_status = indices["status"]

        linhas_invalidas = 0
        agregado: dict[str, dict] = {}

        for linha in leitor:
            if _linha_vazia(linha):
                continue

            if len(linha) != n_colunas:
                linhas_invalidas += 1
                continue

            valores = [campo.strip() for campo in linha]
            regiao = valores[i_regiao]
            produto = valores[i_produto]
            quantidade = _quantidade_valida(valores[i_quantidade])
            preco = _preco_valido(valores[i_preco])

            if not regiao or not produto or quantidade is None or preco is None:
                linhas_invalidas += 1
                continue

            if valores[i_status].lower() != "concluida":
                continue

            regiao_atual = agregado.setdefault(
                regiao, {"quantidade": 0, "vendas": 0.0, "produtos": {}}
            )
            regiao_atual["quantidade"] += quantidade
            regiao_atual["vendas"] += quantidade * preco
            produtos = regiao_atual["produtos"]
            produtos[produto] = produtos.get(produto, 0) + quantidade

    regioes: dict[str, dict] = {}
    for nome in sorted(agregado):
        dados = agregado[nome]
        produto_mais_vendido = min(
            dados["produtos"].items(), key=lambda item: (-item[1], item[0])
        )[0]
        regioes[nome] = {
            "quantidade_total": int(dados["quantidade"]),
            "total_vendas": float(round(dados["vendas"], 2)),
            "produto_mais_vendido": produto_mais_vendido,
        }

    resumo = {
        "regioes": regioes,
        "total_geral": float(
            round(sum(item["total_vendas"] for item in regioes.values()), 2)
        ),
        "linhas_invalidas": int(linhas_invalidas),
    }

    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text(
        json.dumps(resumo, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return resumo


def _linha_vazia(linha: list[str]) -> bool:
    # Registro vazio do csv (linha em branco) ou linha só com espaços.
    return len(linha) == 0 or (len(linha) == 1 and linha[0].strip() == "")


def _quantidade_valida(valor: str) -> int | None:
    try:
        quantidade = int(valor)
    except ValueError:
        return None
    if quantidade <= 0:
        return None
    return quantidade


def _preco_valido(valor: str) -> float | None:
    try:
        preco = float(valor)
    except ValueError:
        return None
    if not math.isfinite(preco) or preco < 0:
        return None
    return preco
