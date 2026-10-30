from __future__ import annotations

import csv
import json
import re
from pathlib import Path

_REQUIRED_COLUMNS = ("produto", "quantidade", "preco_centavos", "status")
_INT_RE = re.compile(r"[+-]?[0-9]+")


def _parse_non_negative_int(raw: str) -> int:
    s = raw.strip()
    if not _INT_RE.fullmatch(s):
        raise ValueError(f"Valor inteiro inválido: {raw!r}")
    value = int(s)
    if value < 0:
        raise ValueError(f"Valor inteiro negativo não permitido: {raw!r}")
    return value


def resumir_vendas(
    entrada: str | Path,
    saida: str | Path,
    minimo_centavos: int = 0,
) -> list[dict]:
    if type(minimo_centavos) is not int or minimo_centavos < 0:
        raise ValueError("minimo_centavos deve ser um int >= 0")

    totais: dict[str, list[int]] = {}

    with open(entrada, mode="r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        try:
            cabecalho = next(reader)
        except StopIteration:
            raise ValueError("Arquivo CSV vazio") from None

        indices: dict[str, int] = {}
        for idx, nome in enumerate(cabecalho):
            if nome not in indices:
                indices[nome] = idx

        for col in _REQUIRED_COLUMNS:
            if col not in indices:
                raise ValueError(f"Coluna obrigatória ausente no cabeçalho: {col!r}")

        idx_produto = indices["produto"]
        idx_quantidade = indices["quantidade"]
        idx_preco = indices["preco_centavos"]
        idx_status = indices["status"]
        max_required_idx = max(idx_produto, idx_quantidade, idx_preco, idx_status)

        for linha in reader:
            if idx_status >= len(linha):
                continue
            if linha[idx_status].strip().lower() != "pago":
                continue

            if max_required_idx >= len(linha):
                raise ValueError("Linha paga com campos obrigatórios faltando")

            produto = linha[idx_produto].strip()
            if not produto:
                raise ValueError("Produto vazio em linha paga")

            quantidade = _parse_non_negative_int(linha[idx_quantidade])
            preco_centavos = _parse_non_negative_int(linha[idx_preco])
            receita = quantidade * preco_centavos

            acumulado = totais.get(produto)
            if acumulado is None:
                totais[produto] = [quantidade, receita]
            else:
                acumulado[0] += quantidade
                acumulado[1] += receita

    resultado = [
        {
            "produto": produto,
            "quantidade": totais[produto][0],
            "receita_centavos": totais[produto][1],
        }
        for produto in sorted(totais)
        if totais[produto][1] >= minimo_centavos
    ]

    conteudo_json = json.dumps(resultado, ensure_ascii=False, indent=2) + "\n"
    with open(saida, mode="w", encoding="utf-8", newline="\n") as out:
        out.write(conteudo_json)

    return resultado
