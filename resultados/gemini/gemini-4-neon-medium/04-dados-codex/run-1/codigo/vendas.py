from __future__ import annotations

import csv
import json
import re
from os import PathLike
from typing import Union

_ASCII_INT_RE = re.compile(r"[+-]?[0-9]+")
_REQUIRED_COLUMNS = ("produto", "quantidade", "preco_centavos", "status")


def _parse_non_negative_int(value: str, field_name: str) -> int:
    text = value.strip()
    if _ASCII_INT_RE.fullmatch(text) is None:
        raise ValueError(f"Valor inválido para {field_name}: {value!r}")
    number = int(text)
    if number < 0:
        raise ValueError(f"Valor negativo para {field_name}: {value!r}")
    return number


def resumir_vendas(
    entrada: Union[str, PathLike[str]],
    saida: Union[str, PathLike[str]],
    minimo_centavos: int = 0,
) -> list[dict]:
    if type(minimo_centavos) is not int or minimo_centavos < 0:
        raise ValueError("minimo_centavos deve ser um int >= 0.")

    totais: dict[str, list[int]] = {}

    with open(entrada, mode="r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header is None:
            raise ValueError("Arquivo CSV vazio.")

        col_index = {name: idx for idx, name in enumerate(header)}
        if not all(col in col_index for col in _REQUIRED_COLUMNS):
            raise ValueError("Cabeçalho sem coluna obrigatória.")

        idx_produto = col_index["produto"]
        idx_quantidade = col_index["quantidade"]
        idx_preco = col_index["preco_centavos"]
        idx_status = col_index["status"]
        max_required_idx = max(idx_produto, idx_quantidade, idx_preco)

        for row in reader:
            row_len = len(row)
            if idx_status >= row_len:
                continue
            if row[idx_status].strip().lower() != "pago":
                continue

            if max_required_idx >= row_len:
                raise ValueError("Campos obrigatórios faltantes em linha paga.")

            produto = row[idx_produto].strip()
            if not produto:
                raise ValueError("Produto vazio em linha paga.")

            quantidade = _parse_non_negative_int(row[idx_quantidade], "quantidade")
            preco = _parse_non_negative_int(row[idx_preco], "preco_centavos")

            acumulado = totais.get(produto)
            if acumulado is None:
                totais[produto] = [quantidade, quantidade * preco]
            else:
                acumulado[0] += quantidade
                acumulado[1] += quantidade * preco

    resultado = [
        {
            "produto": produto,
            "quantidade": dados[0],
            "receita_centavos": dados[1],
        }
        for produto, dados in sorted(totais.items(), key=lambda item: item[0])
        if dados[1] >= minimo_centavos
    ]

    with open(saida, mode="w", encoding="utf-8", newline="\n") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
        f.write("\n")

    return resultado
