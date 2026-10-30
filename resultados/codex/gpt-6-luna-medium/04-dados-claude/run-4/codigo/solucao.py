import csv
import json
import math
import os
import tempfile
from pathlib import Path


_COLUNAS = ("data", "regiao", "produto", "quantidade", "preco_unitario", "status")


def resumir_vendas(entrada: str | Path, saida: str | Path) -> dict:
    """Lê vendas de um CSV, agrega as concluídas e grava o resumo em JSON."""
    entrada = Path(entrada)
    saida = Path(saida)

    regioes: dict = {}
    linhas_invalidas = 0

    # O utf-8-sig aceita tanto UTF-8 puro quanto um BOM inicial. Ler e validar
    # tudo antes de tocar no destino preserva um arquivo de saída em caso de erro.
    with entrada.open("r", encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.reader(arquivo)
        cabecalho = next(leitor, None)
        if cabecalho is None:
            raise ValueError("CSV sem cabeçalho")

        cabecalho = [nome.strip() for nome in cabecalho]
        indices = {}
        for coluna in _COLUNAS:
            if coluna not in cabecalho:
                raise ValueError(f"Coluna obrigatória ausente: {coluna}")
            indices[coluna] = cabecalho.index(coluna)

        for linha in leitor:
            valores = [valor.strip() for valor in linha]
            # csv.reader representa uma linha em branco como []; também ignora
            # registros formados somente por delimitadores sem conteúdo.
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

            reg = regioes.setdefault(
                regiao,
                {"quantidade_total": 0, "vendas": 0.0, "produtos": {}},
            )
            reg["quantidade_total"] += quantidade
            reg["vendas"] += quantidade * preco
            reg["produtos"][produto] = reg["produtos"].get(produto, 0) + quantidade

    saida_regioes = {}
    for regiao in sorted(regioes):
        reg = regioes[regiao]
        produto_mais_vendido = min(
            reg["produtos"], key=lambda nome: (-reg["produtos"][nome], nome)
        )
        saida_regioes[regiao] = {
            "quantidade_total": reg["quantidade_total"],
            "total_vendas": float(round(reg["vendas"], 2)),
            "produto_mais_vendido": produto_mais_vendido,
        }

    resumo = {
        "regioes": saida_regioes,
        "total_geral": float(round(sum(r["total_vendas"] for r in saida_regioes.values()), 2)),
        "linhas_invalidas": linhas_invalidas,
    }

    texto = json.dumps(resumo, ensure_ascii=False, indent=2)
    saida.parent.mkdir(parents=True, exist_ok=True)
    temporario = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=saida.parent, delete=False
        ) as arquivo_temp:
            temporario = Path(arquivo_temp.name)
            arquivo_temp.write(texto)
        os.replace(temporario, saida)
    except Exception:
        if temporario is not None:
            try:
                temporario.unlink(missing_ok=True)
            except OSError:
                pass
        raise

    return resumo
