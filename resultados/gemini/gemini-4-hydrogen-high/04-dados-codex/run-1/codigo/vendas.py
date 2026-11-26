"""Resumo de vendas em CSV para JSON."""

import csv
import json
import re

_REQUIRED_COLUMNS = ("produto", "quantidade", "preco_centavos", "status")
_INT_PATTERN = re.compile(r"[+-]?[0-9]+", re.ASCII)


def _parse_non_negative_int(raw: str, campo: str) -> int:
    """Converte uma célula numérica após strip() em inteiro não negativo."""
    text = raw.strip()
    if not _INT_PATTERN.fullmatch(text):
        raise ValueError(f"Valor inválido para {campo}: {raw!r}")
    value = int(text)
    if value < 0:
        raise ValueError(f"Valor negativo para {campo}: {raw!r}")
    return value


def resumir_vendas(entrada, saida, minimo_centavos: int = 0) -> list[dict]:
    """Lê vendas de um CSV UTF-8, agrega linhas pagas e grava resumo em JSON."""
    if type(minimo_centavos) is not int or minimo_centavos < 0:
        raise ValueError("minimo_centavos deve ser um inteiro >= 0.")

    with open(entrada, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header is None:
            raise ValueError("Arquivo CSV vazio; cabeçalho obrigatório ausente.")

        col_index: dict[str, int] = {}
        for idx, name in enumerate(header):
            if name in _REQUIRED_COLUMNS and name not in col_index:
                col_index[name] = idx

        missing = [col for col in _REQUIRED_COLUMNS if col not in col_index]
        if missing:
            raise ValueError(
                f"Colunas obrigatórias ausentes no cabeçalho: {', '.join(missing)}"
            )

        idx_produto = col_index["produto"]
        idx_quantidade = col_index["quantidade"]
        idx_preco = col_index["preco_centavos"]
        idx_status = col_index["status"]
        min_required_len = max(idx_produto, idx_quantidade, idx_preco, idx_status) + 1

        totals: dict[str, list[int]] = {}
        for row in reader:
            row_len = len(row)
            if idx_status >= row_len or row[idx_status].strip().lower() != "pago":
                continue

            if row_len < min_required_len:
                raise ValueError("Linha paga com campos obrigatórios faltando.")

            produto = row[idx_produto].strip()
            if not produto:
                raise ValueError("Produto vazio em linha paga.")

            quantidade = _parse_non_negative_int(row[idx_quantidade], "quantidade")
            preco = _parse_non_negative_int(row[idx_preco], "preco_centavos")
            receita = quantidade * preco

            entry = totals.get(produto)
            if entry is None:
                totals[produto] = [quantidade, receita]
            else:
                entry[0] += quantidade
                entry[1] += receita

    resultado = []
    for produto in sorted(totals):
        qtd, receita = totals[produto]
        if receita >= minimo_centavos:
            resultado.append(
                {
                    "produto": produto,
                    "quantidade": qtd,
                    "receita_centavos": receita,
                }
            )

    payload = json.dumps(resultado, ensure_ascii=False, indent=2) + "\n"
    with open(saida, "w", encoding="utf-8") as out_file:
        out_file.write(payload)

    return resultado
