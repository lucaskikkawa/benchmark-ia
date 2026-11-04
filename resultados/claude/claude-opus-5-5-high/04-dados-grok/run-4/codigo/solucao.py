"""Consolida chamados por equipe e verifica o SLA de cada prioridade."""

import csv
import json
import re
from datetime import datetime, timedelta

CABECALHO = ["id", "equipe", "aberto_em", "fechado_em", "prioridade"]
PRIORIDADES = ("baixa", "media", "alta")
_UM_MINUTO = timedelta(minutes=1)
_FORMATO_DATA = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}")


def _ler_sla(caminho_sla):
    with open(caminho_sla, encoding="utf-8") as f:
        texto = f.read()
    try:
        dados = json.loads(texto)
    except ValueError as e:
        raise ValueError(f"SLA: JSON inválido: {e}") from e
    if not isinstance(dados, dict) or set(dados) != {"limites_minutos"}:
        raise ValueError("SLA: a raiz deve ter exatamente a chave 'limites_minutos'")
    limites = dados["limites_minutos"]
    if not isinstance(limites, dict) or set(limites) != set(PRIORIDADES):
        raise ValueError("SLA: 'limites_minutos' deve ter exatamente baixa, media e alta")
    for prioridade, limite in limites.items():
        if type(limite) is not int or limite < 1:
            raise ValueError(f"SLA: limite inválido para {prioridade!r}: {limite!r}")
    return dict(limites)


def _ler_data(valor, campo, linha):
    if not _FORMATO_DATA.fullmatch(valor):
        raise ValueError(f"linha {linha}: {campo} fora do formato YYYY-MM-DDTHH:MM: {valor!r}")
    try:
        return datetime.strptime(valor, "%Y-%m-%dT%H:%M")
    except ValueError as e:
        raise ValueError(f"linha {linha}: {campo} inexistente: {valor!r}") from e


def _ler_chamados(caminho_csv):
    with open(caminho_csv, encoding="utf-8", newline="") as f:
        try:
            linhas = list(csv.reader(f))
        except csv.Error as e:
            raise ValueError(f"CSV malformado: {e}") from e

    if not linhas:
        raise ValueError("CSV vazio")
    if linhas[0] != CABECALHO:
        raise ValueError(f"cabeçalho inválido: {linhas[0]!r}")

    chamados = []
    ids_vistos = set()
    for numero, bruto in enumerate(linhas[1:], start=2):
        campos = [c.strip() for c in bruto]
        if not any(campos):
            continue
        if len(campos) != len(CABECALHO):
            raise ValueError(f"linha {numero}: esperado {len(CABECALHO)} colunas, veio {len(campos)}")
        id_, equipe, aberto_em, fechado_em, prioridade = campos
        if not id_:
            raise ValueError(f"linha {numero}: id vazio")
        if not equipe:
            raise ValueError(f"linha {numero}: equipe vazia")
        if id_ in ids_vistos:
            raise ValueError(f"linha {numero}: id duplicado {id_!r}")
        ids_vistos.add(id_)
        if prioridade not in PRIORIDADES:
            raise ValueError(f"linha {numero}: prioridade inválida {prioridade!r}")
        aberto = _ler_data(aberto_em, "aberto_em", numero)
        fechado = _ler_data(fechado_em, "fechado_em", numero)
        if fechado < aberto:
            raise ValueError(f"linha {numero}: fechado_em anterior a aberto_em")
        duracao = (fechado - aberto) // _UM_MINUTO
        chamados.append((id_, equipe, duracao, prioridade))
    return chamados


def consolidar(caminho_csv: str, caminho_sla: str, caminho_saida: str) -> dict:
    """Lê os chamados e o SLA, grava o resumo em JSON e devolve o mesmo dict."""
    limites = _ler_sla(caminho_sla)
    chamados = _ler_chamados(caminho_csv)

    por_equipe = {}
    for id_, equipe, duracao, prioridade in chamados:
        por_equipe.setdefault(equipe, []).append((id_, duracao, prioridade))

    equipes = []
    for equipe in sorted(por_equipe):
        itens = por_equipe[equipe]
        soma = sum(duracao for _, duracao, _ in itens)
        pior_id = min(itens, key=lambda item: (-item[1], item[0]))[0]
        equipes.append({
            "equipe": equipe,
            "chamados": len(itens),
            "estourados": sum(1 for _, duracao, p in itens if duracao > limites[p]),
            "tempo_medio_minutos": soma // len(itens),
            "pior_id": pior_id,
        })

    resultado = {"equipes": equipes}
    texto = json.dumps(resultado, ensure_ascii=False, indent=2) + "\n"
    with open(caminho_saida, "w", encoding="utf-8", newline="") as f:
        f.write(texto)
    return json.loads(texto)
