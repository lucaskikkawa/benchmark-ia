import csv
import json
import re
import sys

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)

try:
    csv.field_size_limit(sys.maxsize)
except OverflowError:
    csv.field_size_limit(2**31 - 1)

NUMERIC_RE = re.compile(r"\A[+-]?[0-9]+\Z")
REQUIRED_COLUMNS = ("produto", "quantidade", "preco_centavos", "status")


def resumir_vendas(entrada, saida, minimo_centavos: int = 0) -> list[dict]:
    if type(minimo_centavos) is not int:
        raise ValueError("minimo_centavos deve ser exatamente do tipo int")
    if minimo_centavos < 0:
        raise ValueError("minimo_centavos deve ser maior ou igual a zero")

    with open(entrada, mode="r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            raise ValueError("Arquivo vazio: cabeçalho ausente")

        idx_map = {}
        for col in REQUIRED_COLUMNS:
            if col in header:
                idx_map[col] = header.index(col)

        if len(idx_map) < len(REQUIRED_COLUMNS):
            stripped_header = [c.strip() for c in header]
            if all(col in stripped_header for col in REQUIRED_COLUMNS):
                idx_map = {col: stripped_header.index(col) for col in REQUIRED_COLUMNS}
            else:
                raise ValueError("Cabeçalho sem coluna obrigatória")

        idx_produto = idx_map["produto"]
        idx_quantidade = idx_map["quantidade"]
        idx_preco = idx_map["preco_centavos"]
        idx_status = idx_map["status"]

        agregado: dict[str, list[int]] = {}

        for row in reader:
            if idx_status >= len(row):
                # Status ausente: linhas com campos faltando são ignoradas se não pagas
                continue

            status_val = row[idx_status].strip().lower()
            if status_val != "pago":
                # Linhas não pagas são ignoradas antes de validar produto e números
                continue

            # Se pagas, campos obrigatórios faltantes são inválidos
            if (
                idx_produto >= len(row)
                or idx_quantidade >= len(row)
                or idx_preco >= len(row)
            ):
                raise ValueError("Linha paga com campos obrigatórios faltantes")

            produto = row[idx_produto].strip()
            if not produto:
                raise ValueError("Produto não pode ficar vazio")

            qtd_str = row[idx_quantidade].strip()
            if not NUMERIC_RE.match(qtd_str):
                raise ValueError(f"Quantidade inválida: {qtd_str!r}")
            qtd = int(qtd_str)
            if qtd < 0:
                raise ValueError(f"Quantidade negativa: {qtd}")

            preco_str = row[idx_preco].strip()
            if not NUMERIC_RE.match(preco_str):
                raise ValueError(f"Preço inválido: {preco_str!r}")
            preco = int(preco_str)
            if preco < 0:
                raise ValueError(f"Preço negativo: {preco}")

            receita_linha = qtd * preco
            if produto in agregado:
                entry = agregado[produto]
                entry[0] += qtd
                entry[1] += receita_linha
            else:
                agregado[produto] = [qtd, receita_linha]

    resultado = []
    for prod in sorted(agregado.keys()):
        qtd_total, receita_total = agregado[prod]
        if receita_total >= minimo_centavos:
            resultado.append(
                {
                    "produto": prod,
                    "quantidade": qtd_total,
                    "receita_centavos": receita_total,
                }
            )

    json_text = json.dumps(resultado, ensure_ascii=False, indent=2) + "\n"

    with open(saida, mode="w", encoding="utf-8", newline="\n") as f:
        f.write(json_text)

    return resultado
