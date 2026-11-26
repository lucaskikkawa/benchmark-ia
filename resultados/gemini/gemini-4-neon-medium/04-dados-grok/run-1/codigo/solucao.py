import csv
import json
import re
from datetime import datetime

_HEADER = ["id", "equipe", "aberto_em", "fechado_em", "prioridade"]
_PRIORIDADES = frozenset({"baixa", "media", "alta"})
_TIMESTAMP_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}$")


def _carregar_sla(caminho_sla: str) -> dict[str, int]:
    with open(caminho_sla, mode="r", encoding="utf-8") as f:
        dados = json.load(f)

    if not isinstance(dados, dict) or set(dados.keys()) != {"limites_minutos"}:
        raise ValueError("SLA deve ser um objeto JSON com exatamente a chave 'limites_minutos'.")

    limites = dados["limites_minutos"]
    if not isinstance(limites, dict) or set(limites.keys()) != _PRIORIDADES:
        raise ValueError("limites_minutos deve conter exatamente as chaves 'baixa', 'media' e 'alta'.")

    resultado: dict[str, int] = {}
    for prioridade, valor in limites.items():
        if not isinstance(valor, int) or isinstance(valor, bool) or valor < 1:
            raise ValueError(f"Limite inválido para prioridade '{prioridade}': {valor!r}.")
        resultado[prioridade] = valor

    return resultado


def _parse_timestamp(valor: str) -> datetime:
    if not _TIMESTAMP_RE.match(valor):
        raise ValueError(f"Timestamp em formato inválido: {valor!r}.")
    return datetime(
        int(valor[0:4]),
        int(valor[5:7]),
        int(valor[8:10]),
        int(valor[11:13]),
        int(valor[14:16]),
    )


def consolidar(caminho_csv: str, caminho_sla: str, caminho_saida: str) -> dict:
    """Lê os chamados e o SLA, grava o resumo em JSON e devolve o mesmo dict."""
    limites = _carregar_sla(caminho_sla)

    ids_vistos: set[str] = set()
    # equipe -> [chamados, estourados, soma_duracao, pior_duracao, pior_id]
    por_equipe: dict[str, list] = {}

    with open(caminho_csv, mode="r", encoding="utf-8", newline="") as f:
        leitor = csv.reader(f)
        cabecalho = next(leitor, None)
        if cabecalho != _HEADER:
            raise ValueError(f"Cabeçalho inválido: {cabecalho!r}.")

        for linha in leitor:
            if not linha or all(campo.strip() == "" for campo in linha):
                continue

            if len(linha) != 5:
                raise ValueError(f"Número de colunas inválido: {len(linha)}.")

            chamado_id, equipe, aberto_str, fechado_str, prioridade = (
                campo.strip() for campo in linha
            )

            if not chamado_id or not equipe:
                raise ValueError("id e equipe não podem ser vazios.")

            if chamado_id in ids_vistos:
                raise ValueError(f"id duplicado: {chamado_id!r}.")
            ids_vistos.add(chamado_id)

            if prioridade not in _PRIORIDADES:
                raise ValueError(f"Prioridade inválida: {prioridade!r}.")

            aberto_dt = _parse_timestamp(aberto_str)
            fechado_dt = _parse_timestamp(fechado_str)
            delta = fechado_dt - aberto_dt
            duracao = delta.days * 1440 + delta.seconds // 60
            if duracao < 0:
                raise ValueError(
                    f"fechado_em ({fechado_str}) anterior a aberto_em ({aberto_str})."
                )

            estourou = 1 if duracao > limites[prioridade] else 0

            if equipe not in por_equipe:
                por_equipe[equipe] = [1, estourou, duracao, duracao, chamado_id]
            else:
                stats = por_equipe[equipe]
                stats[0] += 1
                stats[1] += estourou
                stats[2] += duracao
                if duracao > stats[3] or (duracao == stats[3] and chamado_id < stats[4]):
                    stats[3] = duracao
                    stats[4] = chamado_id

    equipes_resumo = []
    for equipe in sorted(por_equipe):
        chamados, estourados, soma_duracao, _, pior_id = por_equipe[equipe]
        equipes_resumo.append(
            {
                "equipe": equipe,
                "chamados": chamados,
                "estourados": estourados,
                "tempo_medio_minutos": soma_duracao // chamados,
                "pior_id": pior_id,
            }
        )

    resultado = {"equipes": equipes_resumo}
    conteudo = json.dumps(resultado, ensure_ascii=False, indent=2) + "\n"
    with open(caminho_saida, mode="w", encoding="utf-8", newline="\n") as f:
        f.write(conteudo)

    return resultado
