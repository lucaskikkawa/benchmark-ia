from __future__ import annotations

import csv
import json
from pathlib import Path
import re

_INT_RE = re.compile(r"\A[+-]?[0-9]+\Z", re.ASCII)
_REQUIRED_COLUMNS = ("produto", "quantidade", "preco_centavos", "status")


def _parse_non_negative_int(raw: str) -> int:
    s = raw.strip()
    if not _INT_RE.fullmatch(s):
        raise ValueError(f"Valor inteiro inválido: {raw!r}")
    val = int(s)
    if val < 0:
        raise ValueError(f"Valor inteiro negativo não permitido: {raw!r}")
    return val


def resumir_vendas(entrada, saida, minimo_centavos: int = 0) -> list[dict]:
    if type(minimo_centavos) is not int or minimo_centavos < 0:
        raise ValueError("minimo_centavos deve ser um int >= 0")

    entrada_path = Path(entrada)
    saida_path = Path(saida)

    agregado: dict[str, list[int]] = {}

    with entrada_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration as exc:
            raise ValueError("Arquivo CSV vazio") from exc

        col_idx = {name: idx for idx, name in enumerate(header)}
        for req in _REQUIRED_COLUMNS:
            if req not in col_idx:
                raise ValueError(f"Coluna obrigatória ausente: {req}")

        idx_produto = col_idx["produto"]
        idx_quantidade = col_idx["quantidade"]
        idx_preco = col_idx["preco_centavos"]
        idx_status = col_idx["status"]
        max_req_idx = max(idx_produto, idx_quantidade, idx_preco, idx_status)

        for row in reader:
            if len(row) <= idx_status:
                continue
            if row[idx_status].strip().lower() != "pago":
                continue

            if len(row) <= max_req_idx:
                raise ValueError("Linha paga com campos obrigatórios faltando")

            produto = row[idx_produto].strip()
            if not produto:
                raise ValueError("Produto vazio em linha paga")

            quantidade = _parse_non_negative_int(row[idx_quantidade])
            preco_centavos = _parse_non_negative_int(row[idx_preco])
            receita = quantidade * preco_centavos

            item = agregado.get(produto)
            if item is None:
                agregado[produto] = [quantidade, receita]
            else:
                item[0] += quantidade
                item[1] += receita

    resultado = [
        {
            "produto": produto,
            "quantidade": totais[0],
            "receita_centavos": totais[1],
        }
        for produto, totais in sorted(agregado.items(), key=lambda kv: kv[0])
        if totais[1] >= minimo_centavos
    ]

    saida_path.write_text(
        json.dumps(resultado, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    return resultado
