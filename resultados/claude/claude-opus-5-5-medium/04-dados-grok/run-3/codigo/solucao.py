"""Consolidação de chamados por equipe com verificação de SLA."""

import csv
import json
import re
from datetime import datetime

CABECALHO = ["id", "equipe", "aberto_em", "fechado_em", "prioridade"]
PRIORIDADES = ("baixa", "media", "alta")
_RE_DATA = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}")


def _ler_sla(caminho_sla):
    with open(caminho_sla, "r", encoding="utf-8") as f:
        texto = f.read()
    if not texto.strip():
        raise ValueError("SLA vazio")
    dados = json.loads(texto)  # JSONDecodeError é ValueError
    if not isinstance(dados, dict) or set(dados) != {"limites_minutos"}:
        raise ValueError("SLA deve ter exatamente a chave 'limites_minutos'")
    limites = dados["limites_minutos"]
    if not isinstance(limites, dict) or set(limites) != set(PRIORIDADES):
        raise ValueError("limites_minutos deve ter exatamente baixa, media e alta")
    for prioridade, limite in limites.items():
        if type(limite) is not int or limite < 1:
            raise ValueError(f"limite inválido para {prioridade!r}: {limite!r}")
    return dict(limites)


def _data(texto, linha):
    if len(texto) != 16 or not _RE_DATA.fullmatch(texto):
        raise ValueError(f"linha {linha}: data em formato inválido: {texto!r}")
    try:
        return datetime.strptime(texto, "%Y-%m-%dT%H:%M")
    except ValueError as e:
        raise ValueError(f"linha {linha}: data inexistente: {texto!r}") from e


def _ler_chamados(caminho_csv):
    with open(caminho_csv, "r", encoding="utf-8", newline="") as f:
        try:
            linhas = list(csv.reader(f, strict=True))
        except csv.Error as e:
            raise ValueError(f"CSV malformado: {e}") from e

    if not linhas:
        raise ValueError("CSV vazio")
    if linhas[0] != CABECALHO:
        raise ValueError(f"cabeçalho inválido: {linhas[0]!r}")

    chamados = []
    ids = set()
    for numero, bruta in enumerate(linhas[1:], start=2):
        campos = [c.strip() for c in bruta]
        if not any(campos):
            continue
        if len(campos) != len(CABECALHO):
            raise ValueError(f"linha {numero}: esperadas 5 colunas, há {len(campos)}")
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
    limites = _ler_sla(caminho_sla)
    chamados = _ler_chamados(caminho_csv)

    grupos = {}
    for id_, equipe, duracao, prioridade in chamados:
        grupos.setdefault(equipe, []).append((id_, duracao, prioridade))

    equipes = []
    for equipe in sorted(grupos):
        itens = grupos[equipe]
        total = sum(d for _, d, _ in itens)
        pior = min(itens, key=lambda it: (-it[1], it[0]))
        equipes.append({
            "equipe": equipe,
            "chamados": len(itens),
            "estourados": sum(1 for _, d, p in itens if d > limites[p]),
            "tempo_medio_minutos": total // len(itens),
            "pior_id": pior[0],
        })

    resultado = {"equipes": equipes}
    conteudo = json.dumps(resultado, ensure_ascii=False, indent=2) + "\n"
    with open(caminho_saida, "w", encoding="utf-8", newline="") as f:
        f.write(conteudo)
    return json.loads(conteudo)
