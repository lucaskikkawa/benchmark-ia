"""Consolidação de chamados por equipe e verificação de SLA."""

import csv
import json
import re
from datetime import datetime, timedelta


_CABECALHO = ["id", "equipe", "aberto_em", "fechado_em", "prioridade"]
_PRIORIDADES = {"baixa", "media", "alta"}
_FORMATO_DATA = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}")


def _objeto_json(pares):
    objeto = {}
    for chave, valor in pares:
        if chave in objeto:
            raise ValueError(f"Chave duplicada no SLA: {chave}")
        objeto[chave] = valor
    return objeto


def _ler_sla(caminho):
    with open(caminho, encoding="utf-8") as arquivo:
        sla = json.load(arquivo, object_pairs_hook=_objeto_json)
    if type(sla) is not dict or set(sla) != {"limites_minutos"}:
        raise ValueError("SLA deve conter apenas limites_minutos")
    limites = sla["limites_minutos"]
    if type(limites) is not dict or set(limites) != _PRIORIDADES:
        raise ValueError("Limites devem conter exatamente baixa, media e alta")
    if any(type(limite) is not int or limite < 1 for limite in limites.values()):
        raise ValueError("Cada limite deve ser um inteiro positivo")
    return limites


def _ler_data(valor):
    if _FORMATO_DATA.fullmatch(valor) is None:
        raise ValueError(f"Formato de data inválido: {valor!r}")
    return datetime.strptime(valor, "%Y-%m-%dT%H:%M")


def consolidar(caminho_csv: str, caminho_sla: str, caminho_saida: str) -> dict:
    """Lê os chamados e o SLA, grava o resumo em JSON e devolve o mesmo dict."""
    limites = _ler_sla(caminho_sla)
    equipes = {}
    ids = set()

    with open(caminho_csv, encoding="utf-8", newline="") as arquivo:
        leitor = csv.reader(arquivo, strict=True)
        try:
            if next(leitor, None) != _CABECALHO:
                raise ValueError("Cabeçalho CSV inválido ou ausente")
            for linha in leitor:
                campos = [campo.strip() for campo in linha]
                if not any(campos):
                    continue
                if len(campos) != 5:
                    raise ValueError("Cada chamado deve ter cinco campos")
                identificador, equipe, abertura, fechamento, prioridade = campos
                if not identificador or not equipe:
                    raise ValueError("Id e equipe são obrigatórios")
                if identificador in ids:
                    raise ValueError(f"Id duplicado: {identificador!r}")
                if prioridade not in _PRIORIDADES:
                    raise ValueError(f"Prioridade inválida: {prioridade!r}")
                aberto_em = _ler_data(abertura)
                fechado_em = _ler_data(fechamento)
                if fechado_em < aberto_em:
                    raise ValueError("Fechamento anterior à abertura")
                duracao = (fechado_em - aberto_em) // timedelta(minutes=1)
                ids.add(identificador)

                if equipe not in equipes:
                    equipes[equipe] = {
                        "chamados": 0,
                        "estourados": 0,
                        "soma": 0,
                        "pior_duracao": -1,
                        "pior_id": identificador,
                    }
                resumo = equipes[equipe]
                resumo["chamados"] += 1
                resumo["estourados"] += int(duracao > limites[prioridade])
                resumo["soma"] += duracao
                if duracao > resumo["pior_duracao"] or (
                    duracao == resumo["pior_duracao"]
                    and identificador < resumo["pior_id"]
                ):
                    resumo["pior_duracao"] = duracao
                    resumo["pior_id"] = identificador
        except csv.Error as erro:
            raise ValueError(f"CSV inválido: {erro}") from erro

    resultado = {"equipes": []}
    for equipe in sorted(equipes):
        resumo = equipes[equipe]
        resultado["equipes"].append({
            "equipe": equipe,
            "chamados": resumo["chamados"],
            "estourados": resumo["estourados"],
            "tempo_medio_minutos": resumo["soma"] // resumo["chamados"],
            "pior_id": resumo["pior_id"],
        })
    with open(caminho_saida, "w", encoding="utf-8", newline="\n") as arquivo:
        arquivo.write(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n")
    return resultado
