"""Consolidação de chamados por equipe com verificação de SLA."""

import csv
import io
import json
import re
from datetime import datetime

CABECALHO = ["id", "equipe", "aberto_em", "fechado_em", "prioridade"]
PRIORIDADES = ("baixa", "media", "alta")
_RE_DATA = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}")


def _ler_texto(caminho: str) -> str:
    with open(caminho, "r", encoding="utf-8", newline="") as f:
        return f.read()


def _validar_sla(texto: str) -> dict:
    if not texto.strip():
        raise ValueError("SLA vazio")
    try:
        dados = json.loads(texto)
    except json.JSONDecodeError as e:
        raise ValueError(f"SLA JSON inválido: {e}") from None
    if not isinstance(dados, dict) or set(dados) != {"limites_minutos"}:
        raise ValueError("SLA deve ter exatamente a chave 'limites_minutos'")
    limites = dados["limites_minutos"]
    if not isinstance(limites, dict) or set(limites) != set(PRIORIDADES):
        raise ValueError("limites_minutos deve ter exatamente baixa, media e alta")
    for prioridade, valor in limites.items():
        if type(valor) is not int or valor < 1:
            raise ValueError(f"limite inválido para {prioridade!r}: {valor!r}")
    return dict(limites)


def _data(valor: str, linha: int) -> datetime:
    if len(valor) != 16 or not _RE_DATA.fullmatch(valor):
        raise ValueError(f"linha {linha}: data em formato inválido: {valor!r}")
    try:
        return datetime.strptime(valor, "%Y-%m-%dT%H:%M")
    except ValueError:
        raise ValueError(f"linha {linha}: data inexistente: {valor!r}") from None


def _ler_chamados(texto: str) -> list:
    if not texto:
        raise ValueError("CSV vazio")
    if texto.startswith("﻿"):
        raise ValueError("CSV com BOM: cabeçalho inválido")
    try:
        linhas = list(csv.reader(io.StringIO(texto, newline=""), strict=True))
    except csv.Error as e:
        raise ValueError(f"CSV malformado: {e}") from None
    if not linhas or linhas[0] != CABECALHO:
        raise ValueError("cabeçalho ausente ou diferente do esperado")

    chamados = []
    ids = set()
    for numero, bruta in enumerate(linhas[1:], start=2):
        campos = [c.strip() for c in bruta]
        if not any(campos):
            continue
        if len(campos) != len(CABECALHO):
            raise ValueError(f"linha {numero}: esperadas 5 colunas, obtidas {len(campos)}")
        id_, equipe, aberto, fechado, prioridade = campos
        if not id_:
            raise ValueError(f"linha {numero}: id vazio")
        if not equipe:
            raise ValueError(f"linha {numero}: equipe vazia")
        if id_ in ids:
            raise ValueError(f"linha {numero}: id duplicado {id_!r}")
        ids.add(id_)
        inicio = _data(aberto, numero)
        fim = _data(fechado, numero)
        if fim < inicio:
            raise ValueError(f"linha {numero}: fechado_em anterior a aberto_em")
        if prioridade not in PRIORIDADES:
            raise ValueError(f"linha {numero}: prioridade inválida {prioridade!r}")
        duracao = int((fim - inicio).total_seconds()) // 60
        chamados.append((id_, equipe, duracao, prioridade))
    return chamados


def consolidar(caminho_csv: str, caminho_sla: str, caminho_saida: str) -> dict:
    """Lê os chamados e o SLA, grava o resumo em JSON e devolve o mesmo dict."""
    texto_csv = _ler_texto(caminho_csv)
    texto_sla = _ler_texto(caminho_sla)
    limites = _validar_sla(texto_sla)
    chamados = _ler_chamados(texto_csv)

    por_equipe = {}
    for id_, equipe, duracao, prioridade in chamados:
        por_equipe.setdefault(equipe, []).append((id_, duracao, prioridade))

    equipes = []
    for equipe in sorted(por_equipe):
        itens = por_equipe[equipe]
        soma = sum(d for _, d, _ in itens)
        pior = min(itens, key=lambda item: (-item[1], item[0]))
        equipes.append({
            "equipe": equipe,
            "chamados": len(itens),
            "estourados": sum(1 for _, d, p in itens if d > limites[p]),
            "tempo_medio_minutos": soma // len(itens),
            "pior_id": pior[0],
        })

    resultado = {"equipes": equipes}
    conteudo = json.dumps(resultado, ensure_ascii=False, indent=2) + "\n"
    with open(caminho_saida, "w", encoding="utf-8", newline="") as f:
        f.write(conteudo)
    return json.loads(conteudo)
