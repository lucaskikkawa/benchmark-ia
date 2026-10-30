import csv
import json
import re
from pathlib import Path
from typing import Union

_NUM_PATTERN = re.compile(r"^[+-]?[0-9]+$", re.ASCII)
_REQUIRED_COLUMNS = ("produto", "quantidade", "preco_centavos", "status")


def _parse_non_negative_int(val: str) -> int:
    s = val.strip()
    if not _NUM_PATTERN.fullmatch(s):
        raise ValueError(f"Valor numérico inválido: {val!r}")
    num = int(s)
    if num < 0:
        raise ValueError(f"Valor numérico não pode ser negativo: {val!r}")
    return num


def resumir_vendas(
    entrada: Union[str, Path],
    saida: Union[str, Path],
    minimo_centavos: int = 0,
) -> list[dict]:
    if type(minimo_centavos) is not int:
        raise ValueError(f"minimo_centavos deve ser int, recebido {type(minimo_centavos).__name__}")
    if minimo_centavos < 0:
        raise ValueError(f"minimo_centavos não pode ser negativo: {minimo_centavos}")

    with open(entrada, mode="r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            raise ValueError("Arquivo CSV vazio: cabeçalho obrigatório ausente")

        col_indices = {}
        for col in _REQUIRED_COLUMNS:
            try:
                col_indices[col] = header.index(col)
            except ValueError:
                raise ValueError(f"Coluna obrigatória ausente no cabeçalho: {col!r}")

        idx_status = col_indices["status"]
        idx_produto = col_indices["produto"]
        idx_quantidade = col_indices["quantidade"]
        idx_preco = col_indices["preco_centavos"]

        # Agregação: produto -> [quantidade_total, receita_centavos_total]
        totais: dict[str, list[int]] = {}

        for row in reader:
            # Linhas com campos faltando são ignoradas se não pagas
            if len(row) <= idx_status:
                continue

            status = row[idx_status].strip().lower()
            if status != "pago":
                continue

            # Se pagas, campos obrigatórios faltantes são inválidos
            if (
                len(row) <= idx_produto
                or len(row) <= idx_quantidade
                or len(row) <= idx_preco
            ):
                raise ValueError("Linha paga com campos obrigatórios ausentes")

            produto = row[idx_produto].strip()
            if not produto:
                raise ValueError("Linha paga com produto vazio")

            quantidade = _parse_non_negative_int(row[idx_quantidade])
            preco_centavos = _parse_non_negative_int(row[idx_preco])

            receita_item = quantidade * preco_centavos

            if produto not in totais:
                totais[produto] = [quantidade, receita_item]
            else:
                totais[produto][0] += quantidade
                totais[produto][1] += receita_item

    resultado: list[dict] = []
    for prod in sorted(totais.keys()):
        qtd, receita = totais[prod]
        if receita >= minimo_centavos:
            resultado.append({
                "produto": prod,
                "quantidade": qtd,
                "receita_centavos": receita,
            })

    # Valide tudo antes de criar/sobrescrever a saída
    json_bytes_str = json.dumps(resultado, ensure_ascii=False, indent=2) + "\n"

    with open(saida, mode="w", encoding="utf-8", newline="\n") as f:
        f.write(json_bytes_str)

    return resultado
