"""Consolidação de chamados por equipe com verificação de SLA."""

import csv
import json
import re
from datetime import datetime

CABECALHO = ["id", "equipe", "aberto_em", "fechado_em", "prioridade"]
PRIORIDADES = ("baixa", "media", "alta")
_RE_DATA = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}")


def _ler_data(texto: str) -> datetime:
    if len(texto) != 16 or not _RE_DATA.fullmatch(texto):
        raise ValueError(f"data em formato inválido: {texto!r}")
    return datetime(
        int(texto[0:4]),
        int(texto[5:7]),
        int(texto[8:10]),
        int(texto[11:13]),
        int(texto[14:16]),
    )


def _sem_duplicatas(pares):
    objeto = {}
    for chave, valor in pares:
        if chave in objeto:
            raise ValueError(f"chave duplicada no SLA: {chave!r}")
        objeto[chave] = valor
    return objeto


def _rejeitar_constante(nome):
    raise ValueError(f"constante inválida no SLA: {nome}")


def _ler_sla(caminho_sla: str) -> dict:
    with open(caminho_sla, encoding="utf-8") as arquivo:
        texto = arquivo.read()
    dados = json.loads(
        texto,
        object_pairs_hook=_sem_duplicatas,
        parse_constant=_rejeitar_constante,
    )
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
    with open(caminho_csv, encoding="utf-8", newline="") as arquivo:
        try:
            linhas = list(csv.reader(arquivo, strict=True))
        except csv.Error as erro:
            raise ValueError(f"CSV malformado: {erro}") from erro

    if not linhas or linhas[0] != CABECALHO:
        raise ValueError("cabeçalho ausente ou diferente do esperado")

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
        if prioridade not in PRIORIDADES:
            raise ValueError(f"linha {numero}: prioridade inválida {prioridade!r}")
        aberto = _ler_data(aberto_em)
        fechado = _ler_data(fechado_em)
        if fechado < aberto:
            raise ValueError(f"linha {numero}: fechado_em anterior a aberto_em")
        delta = fechado - aberto
        duracao = delta.days * 1440 + delta.seconds // 60
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
        equipes.append(
            {
                "equipe": equipe,
                "chamados": len(itens),
                "estourados": sum(
                    1 for _, duracao, prioridade in itens if duracao > limites[prioridade]
                ),
                "tempo_medio_minutos": soma // len(itens),
                "pior_id": pior_id,
            }
        )

    resultado = {"equipes": equipes}
    conteudo = json.dumps(resultado, ensure_ascii=False, indent=2) + "\n"
    with open(caminho_saida, "w", encoding="utf-8", newline="") as arquivo:
        arquivo.write(conteudo)
    return json.loads(conteudo)
