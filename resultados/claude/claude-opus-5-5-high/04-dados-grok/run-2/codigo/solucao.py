"""Consolidação de chamados por equipe com verificação de SLA."""

import csv
import json
import re
from datetime import datetime

CABECALHO = ["id", "equipe", "aberto_em", "fechado_em", "prioridade"]
PRIORIDADES = ("baixa", "media", "alta")
_FORMATO_DATA = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}")


def _ler_data(texto: str) -> datetime:
    if len(texto) != 16 or not _FORMATO_DATA.fullmatch(texto):
        raise ValueError(f"data em formato inválido: {texto!r}")
    try:
        return datetime(
            int(texto[0:4]),
            int(texto[5:7]),
            int(texto[8:10]),
            int(texto[11:13]),
            int(texto[14:16]),
        )
    except ValueError as exc:
        raise ValueError(f"data inexistente: {texto!r}") from exc


def _ler_sla(caminho_sla: str) -> dict:
    with open(caminho_sla, encoding="utf-8") as arq:
        texto = arq.read()
    try:
        dados = json.loads(texto)
    except ValueError as exc:
        raise ValueError(f"JSON de SLA inválido: {exc}") from exc

    if not isinstance(dados, dict) or set(dados) != {"limites_minutos"}:
        raise ValueError("SLA deve ter exatamente a chave 'limites_minutos'")
    limites = dados["limites_minutos"]
    if not isinstance(limites, dict) or set(limites) != set(PRIORIDADES):
        raise ValueError("limites_minutos deve ter exatamente baixa, media e alta")
    for prioridade, limite in limites.items():
        if type(limite) is not int or limite < 1:
            raise ValueError(f"limite inválido para {prioridade!r}: {limite!r}")
    return dict(limites)


def _ler_chamados(caminho_csv: str) -> list:
    with open(caminho_csv, encoding="utf-8", newline="") as arq:
        try:
            linhas = list(csv.reader(arq))
        except csv.Error as exc:
            raise ValueError(f"CSV inválido: {exc}") from exc

    if not linhas:
        raise ValueError("arquivo CSV vazio")
    if linhas[0] != CABECALHO:
        raise ValueError(f"cabeçalho inválido: {linhas[0]!r}")

    chamados = []
    ids_vistos = set()
    for numero, linha in enumerate(linhas[1:], start=2):
        campos = [campo.strip() for campo in linha]
        if all(campo == "" for campo in campos):
            continue
        if len(campos) != len(CABECALHO):
            raise ValueError(f"linha {numero}: esperadas 5 colunas, há {len(campos)}")

        id_, equipe, aberto_em, fechado_em, prioridade = campos
        if not id_:
            raise ValueError(f"linha {numero}: id vazio")
        if not equipe:
            raise ValueError(f"linha {numero}: equipe vazia")
        if id_ in ids_vistos:
            raise ValueError(f"linha {numero}: id duplicado {id_!r}")
        ids_vistos.add(id_)

        aberto = _ler_data(aberto_em)
        fechado = _ler_data(fechado_em)
        if fechado < aberto:
            raise ValueError(f"linha {numero}: fechado_em anterior a aberto_em")
        if prioridade not in PRIORIDADES:
            raise ValueError(f"linha {numero}: prioridade inválida {prioridade!r}")

        duracao = int((fechado - aberto).total_seconds()) // 60
        chamados.append((id_, equipe, duracao, prioridade))
    return chamados


def consolidar(caminho_csv: str, caminho_sla: str, caminho_saida: str) -> dict:
    """Lê os chamados e o SLA, grava o resumo em JSON e devolve o mesmo dict."""
    chamados = _ler_chamados(caminho_csv)
    limites = _ler_sla(caminho_sla)

    por_equipe = {}
    for id_, equipe, duracao, prioridade in chamados:
        por_equipe.setdefault(equipe, []).append((id_, duracao, prioridade))

    equipes = []
    for equipe in sorted(por_equipe):
        itens = por_equipe[equipe]
        soma = sum(duracao for _, duracao, _ in itens)
        estourados = sum(1 for _, duracao, p in itens if duracao > limites[p])
        pior_id = min(itens, key=lambda item: (-item[1], item[0]))[0]
        equipes.append(
            {
                "equipe": equipe,
                "chamados": len(itens),
                "estourados": estourados,
                "tempo_medio_minutos": soma // len(itens),
                "pior_id": pior_id,
            }
        )

    resultado = {"equipes": equipes}
    texto = json.dumps(resultado, ensure_ascii=False, indent=2) + "\n"
    with open(caminho_saida, "w", encoding="utf-8", newline="") as arq:
        arq.write(texto)
    return json.loads(texto)
