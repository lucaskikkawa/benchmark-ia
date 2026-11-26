import csv
import json
from pathlib import Path
import re

_ASCII_INT_RE = re.compile(r"[+-]?[0-9]+")
_REQUIRED_COLUMNS = ("produto", "quantidade", "preco_centavos", "status")


def _parse_non_negative_int(raw: str, field_name: str) -> int:
    text = raw.strip()
    if not _ASCII_INT_RE.fullmatch(text):
        raise ValueError(f"Valor inteiro inválido para {field_name}: {raw!r}")
    value = int(text)
    if value < 0:
        raise ValueError(f"Valor negativo não permitido para {field_name}: {value}")
    return value


def resumir_vendas(entrada, saida, minimo_centavos: int = 0) -> list[dict]:
    if type(minimo_centavos) is not int:
        raise ValueError("minimo_centavos deve ser exatamente int")
    if minimo_centavos < 0:
        raise ValueError("minimo_centavos deve ser >= 0")

    entrada_path = Path(entrada)
    saida_path = Path(saida)

    totais: dict[str, list[int]] = {}

    with entrada_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header is None:
            raise ValueError("Arquivo CSV vazio; cabeçalho obrigatório ausente")

        col_index = {name: idx for idx, name in enumerate(header)}
        missing_cols = [col for col in _REQUIRED_COLUMNS if col not in col_index]
        if missing_cols:
            raise ValueError(f"Colunas obrigatórias ausentes: {', '.join(missing_cols)}")

        idx_produto = col_index["produto"]
        idx_quantidade = col_index["quantidade"]
        idx_preco = col_index["preco_centavos"]
        idx_status = col_index["status"]

        for row in reader:
            if idx_status >= len(row):
                continue
            if row[idx_status].strip().lower() != "pago":
                continue

            if idx_produto >= len(row) or idx_quantidade >= len(row) or idx_preco >= len(row):
                raise ValueError("Linha paga com campos obrigatórios faltantes")

            produto = row[idx_produto].strip()
            if not produto:
                raise ValueError("Produto vazio em linha paga")

            quantidade = _parse_non_negative_int(row[idx_quantidade], "quantidade")
            preco_centavos = _parse_non_negative_int(row[idx_preco], "preco_centavos")
            receita = quantidade * preco_centavos

            acc = totais.get(produto)
            if acc is None:
                totais[produto] = [quantidade, receita]
            else:
                acc[0] += quantidade
                acc[1] += receita

    resultado = [
        {
            "produto": produto,
            "quantidade": qtd,
            "receita_centavos": receita,
        }
        for produto, (qtd, receita) in sorted(totais.items(), key=lambda item: item[0])
        if receita >= minimo_centavos
    ]

    payload = json.dumps(resultado, ensure_ascii=False, indent=2) + "\n"
    with saida_path.open("w", encoding="utf-8", newline="\n") as f:
        f.write(payload)

    return resultado
