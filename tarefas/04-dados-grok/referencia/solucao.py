"""Consolida chamados CSV com o SLA em JSON."""

import csv
import json
from datetime import datetime, timedelta

_CAMPOS = ["id", "equipe", "aberto_em", "fechado_em", "prioridade"]
_PRIORIDADES = ("baixa", "media", "alta")
_FORMATO = "%Y-%m-%dT%H:%M"


def consolidar(caminho_csv: str, caminho_sla: str, caminho_saida: str) -> dict:
    """Lê chamados e SLA, grava o resumo JSON e devolve o mesmo dict.

    Estouro é duração estritamente maior que o limite. A média é a divisão
    inteira das durações. Empate de pior chamado: menor id lexicográfico.
    """
    limites = _ler_sla(caminho_sla)
    chamados = _ler_chamados(caminho_csv)
    resumo = _resumir(chamados, limites)
    texto = json.dumps(resumo, ensure_ascii=False, indent=2) + "\n"
    with open(caminho_saida, "w", encoding="utf-8", newline="\n") as arquivo:
        arquivo.write(texto)
    return resumo


def _ler_sla(caminho: str) -> dict[str, int]:
    with open(caminho, encoding="utf-8") as arquivo:
        dados = json.load(arquivo)
    if not isinstance(dados, dict) or set(dados) != {"limites_minutos"}:
        raise ValueError("sla invalido")
    limites = dados["limites_minutos"]
    if not isinstance(limites, dict) or set(limites) != set(_PRIORIDADES):
        raise ValueError("sla invalido")
    saida = {}
    for nome in _PRIORIDADES:
        valor = limites[nome]
        if isinstance(valor, bool) or not isinstance(valor, int) or valor < 1:
            raise ValueError("sla invalido")
        saida[nome] = valor
    return saida


def _ler_chamados(caminho: str) -> list[dict]:
    with open(caminho, encoding="utf-8", newline="") as arquivo:
        leitor = csv.reader(arquivo)
        try:
            cabecalho = next(leitor)
        except StopIteration as exc:
            raise ValueError("csv vazio") from exc
        if cabecalho != _CAMPOS:
            raise ValueError("cabecalho invalido")
        vistos = set()
        chamados = []
        for numero, linha in enumerate(leitor, start=2):
            if not linha or all(not celula.strip() for celula in linha):
                continue
            if len(linha) != len(_CAMPOS):
                raise ValueError(f"linha {numero} invalida")
            identificador, equipe, aberto, fechado, prioridade = (
                celula.strip() for celula in linha
            )
            if not identificador or not equipe:
                raise ValueError(f"linha {numero} invalida")
            if identificador in vistos:
                raise ValueError(f"id duplicado na linha {numero}")
            vistos.add(identificador)
            if prioridade not in _PRIORIDADES:
                raise ValueError(f"prioridade invalida na linha {numero}")
            inicio = _instante(aberto, numero)
            fim = _instante(fechado, numero)
            if fim < inicio:
                raise ValueError(f"intervalo invalido na linha {numero}")
            chamados.append(
                {
                    "id": identificador,
                    "equipe": equipe,
                    "prioridade": prioridade,
                    "duracao": (fim - inicio) // timedelta(minutes=1),
                }
            )
        return chamados


def _instante(texto: str, numero: int) -> datetime:
    if len(texto) != 16:
        raise ValueError(f"data invalida na linha {numero}")
    try:
        return datetime.strptime(texto, _FORMATO)
    except ValueError as exc:
        raise ValueError(f"data invalida na linha {numero}") from exc


def _resumir(chamados: list[dict], limites: dict[str, int]) -> dict:
    por_equipe: dict[str, list[dict]] = {}
    for chamado in chamados:
        por_equipe.setdefault(chamado["equipe"], []).append(chamado)
    equipes = []
    for equipe in sorted(por_equipe):
        itens = por_equipe[equipe]
        duracoes = [item["duracao"] for item in itens]
        pior = min(itens, key=lambda item: (-item["duracao"], item["id"]))
        equipes.append(
            {
                "equipe": equipe,
                "chamados": len(itens),
                "estourados": sum(
                    1 for item in itens if item["duracao"] > limites[item["prioridade"]]
                ),
                "tempo_medio_minutos": sum(duracoes) // len(duracoes),
                "pior_id": pior["id"],
            }
        )
    return {"equipes": equipes}
