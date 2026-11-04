from __future__ import annotations

import csv
import json
import re
from pathlib import Path

_REQUIRED_COLUMNS = ("produto", "quantidade", "preco_centavos", "status")
_INT_RE = re.compile(r"\A[+-]?[0-9]+\Z", re.ASCII)


def resumir_vendas(
    entrada: str | Path,
    saida: str | Path,
    minimo_centavos: int = 0,
) -> list[dict]:
    if type(minimo_centavos) is not int or minimo_centavos < 0:
        raise ValueError("minimo_centavos deve ser exatamente um int >= 0")

    caminho_entrada = Path(entrada)
    caminho_saida = Path(saida)

    totais: dict[str, list[int]] = {}
    match_int = _INT_RE.match

    with open(caminho_entrada, mode="r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            raise ValueError("Arquivo CSV vazio ou sem cabeçalho") from None

        col_idx = {col: idx for idx, col in enumerate(header)}
        for req in _REQUIRED_COLUMNS:
            if req not in col_idx:
                raise ValueError(f"Coluna obrigatória ausente no cabeçalho: {req}")

        idx_produto = col_idx["produto"]
        idx_quantidade = col_idx["quantidade"]
        idx_preco = col_idx["preco_centavos"]
        idx_status = col_idx["status"]
        max_req_idx = max(idx_produto, idx_quantidade, idx_preco, idx_status)

        for row in reader:
            row_len = len(row)
            if idx_status >= row_len:
                continue

            if row[idx_status].strip().lower() != "pago":
                continue

            if max_req_idx >= row_len:
                raise ValueError("Linha paga com campos obrigatórios faltando")

            produto = row[idx_produto].strip()
            if not produto:
                raise ValueError("Produto vazio em linha paga")

            s_qtd = row[idx_quantidade].strip()
            if match_int(s_qtd) is None:
                raise ValueError(f"Quantidade inválida: {row[idx_quantidade]!r}")
            qtd = int(s_qtd)
            if qtd < 0:
                raise ValueError(f"Quantidade negativa: {row[idx_quantidade]!r}")

            s_preco = row[idx_preco].strip()
            if match_int(s_preco) is None:
                raise ValueError(f"Preço inválido: {row[idx_preco]!r}")
            preco = int(s_preco)
            if preco < 0:
                raise ValueError(f"Preço negativo: {row[idx_preco]!r}")

            receita_item = qtd * preco
            acumulado = totais.get(produto)
            if acumulado is None:
                totais[produto] = [qtd, receita_item]
            else:
                acumulado[0] += qtd
                acumulado[1] += receita_item

    resultado = [
        {
            "produto": produto,
            "quantidade": valores[0],
            "receita_centavos": valores[1],
        }
        for produto, valores in sorted(totais.items())
        if valores[1] >= minimo_centavos
    ]

    conteudo_json = json.dumps(resultado, ensure_ascii=False, indent=2) + "\n"
    with open(caminho_saida, mode="w", encoding="utf-8", newline="\n") as out_f:
        out_f.write(conteudo_json)

    return resultado
