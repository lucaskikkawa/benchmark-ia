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
            raise ValueError("Chave duplicada no JSON de SLA")
        objeto[chave] = valor
    return objeto


def _ler_sla(caminho):
    with open(caminho, encoding="utf-8") as arquivo:
        sla = json.load(arquivo, object_pairs_hook=_objeto_json)

    if not isinstance(sla, dict) or set(sla) != {"limites_minutos"}:
        raise ValueError("SLA deve conter somente limites_minutos")
    limites = sla["limites_minutos"]
    if not isinstance(limites, dict) or set(limites) != _PRIORIDADES:
        raise ValueError("Limites devem conter baixa, media e alta")
    if any(type(limite) is not int or limite < 1 for limite in limites.values()):
        raise ValueError("Cada limite deve ser um inteiro positivo")
    return limites


def _ler_data(valor):
    if _FORMATO_DATA.fullmatch(valor) is None:
        raise ValueError("Data deve usar o formato YYYY-MM-DDTHH:MM")
    return datetime.fromisoformat(valor)


def consolidar(caminho_csv: str, caminho_sla: str, caminho_saida: str) -> dict:
    """Lê os chamados e o SLA, grava o resumo em JSON e devolve o mesmo dict."""
    limites = _ler_sla(caminho_sla)
    equipes = {}
    ids = set()

    with open(caminho_csv, encoding="utf-8", newline="") as arquivo:
        leitor = csv.reader(arquivo, strict=True)
        try:
            if next(leitor, None) != _CABECALHO:
                raise ValueError("Cabeçalho CSV inválido")

            for linha in leitor:
                campos = [campo.strip() for campo in linha]
                if not any(campos):
                    continue
                if len(campos) != 5:
                    raise ValueError("Cada chamado deve ter cinco colunas")

                identificador, equipe, aberto, fechado, prioridade = campos
                if not identificador or not equipe:
                    raise ValueError("Id e equipe não podem ser vazios")
                if identificador in ids:
                    raise ValueError("Id duplicado: " + identificador)
                if prioridade not in _PRIORIDADES:
                    raise ValueError("Prioridade inválida: " + prioridade)

                inicio = _ler_data(aberto)
                fim = _ler_data(fechado)
                if fim < inicio:
                    raise ValueError("Fechamento anterior à abertura")
                duracao = (fim - inicio) // timedelta(minutes=1)
                ids.add(identificador)

                if equipe not in equipes:
                    equipes[equipe] = {
                        "chamados": 0,
                        "estourados": 0,
                        "soma": 0,
                        "maior_duracao": -1,
                        "pior_id": identificador,
                    }
                dados = equipes[equipe]
                dados["chamados"] += 1
                dados["estourados"] += int(duracao > limites[prioridade])
                dados["soma"] += duracao
                if duracao > dados["maior_duracao"] or (
                    duracao == dados["maior_duracao"]
                    and identificador < dados["pior_id"]
                ):
                    dados["maior_duracao"] = duracao
                    dados["pior_id"] = identificador
        except csv.Error as erro:
            raise ValueError("CSV inválido") from erro

    resultado = {"equipes": []}
    for equipe in sorted(equipes):
        dados = equipes[equipe]
        resultado["equipes"].append({
            "equipe": equipe,
            "chamados": dados["chamados"],
            "estourados": dados["estourados"],
            "tempo_medio_minutos": dados["soma"] // dados["chamados"],
            "pior_id": dados["pior_id"],
        })

    with open(caminho_saida, "w", encoding="utf-8", newline="\n") as arquivo:
        arquivo.write(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n")
    return resultado
