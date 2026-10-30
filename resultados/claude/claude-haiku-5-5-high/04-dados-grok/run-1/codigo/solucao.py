import csv
import json
import re
from datetime import datetime, timedelta

CABECALHO = ["id", "equipe", "aberto_em", "fechado_em", "prioridade"]
PRIORIDADES = ("baixa", "media", "alta")
FORMATO_DATA = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}")
UM_MINUTO = timedelta(minutes=1)


def _ler_data(texto: str) -> datetime:
    if not FORMATO_DATA.fullmatch(texto):
        raise ValueError(f"data fora do formato YYYY-MM-DDTHH:MM: {texto!r}")
    try:
        return datetime.strptime(texto, "%Y-%m-%dT%H:%M")
    except ValueError as erro:
        raise ValueError(f"data inexistente: {texto!r}") from erro


def _ler_chamados(caminho_csv: str) -> list[dict]:
    with open(caminho_csv, encoding="utf-8", newline="") as arquivo:
        leitor = csv.reader(arquivo)
        try:
            cabecalho = next(leitor)
        except StopIteration:
            raise ValueError("CSV vazio ou sem cabeçalho") from None
        if cabecalho != CABECALHO:
            raise ValueError(f"cabeçalho diferente do esperado: {cabecalho!r}")

        chamados = []
        ids = set()
        for linha in leitor:
            if not any(campo.strip() for campo in linha):
                continue
            if len(linha) != len(CABECALHO):
                raise ValueError(f"número de colunas inválido: {linha!r}")

            id_, equipe, aberto, fechado, prioridade = (c.strip() for c in linha)
            if not id_:
                raise ValueError("id vazio")
            if not equipe:
                raise ValueError(f"equipe vazia no chamado {id_!r}")
            if id_ in ids:
                raise ValueError(f"id duplicado: {id_!r}")
            ids.add(id_)

            inicio = _ler_data(aberto)
            fim = _ler_data(fechado)
            if fim < inicio:
                raise ValueError(f"fechado_em anterior a aberto_em no chamado {id_!r}")
            if prioridade not in PRIORIDADES:
                raise ValueError(f"prioridade inválida no chamado {id_!r}: {prioridade!r}")

            chamados.append({
                "id": id_,
                "equipe": equipe,
                "duracao": (fim - inicio) // UM_MINUTO,
                "prioridade": prioridade,
            })
    return chamados


def _ler_sla(caminho_sla: str) -> dict:
    with open(caminho_sla, encoding="utf-8") as arquivo:
        dados = json.load(arquivo)
    if not isinstance(dados, dict) or set(dados) != {"limites_minutos"}:
        raise ValueError("SLA deve ter exatamente a chave 'limites_minutos'")

    limites = dados["limites_minutos"]
    if not isinstance(limites, dict) or set(limites) != set(PRIORIDADES):
        raise ValueError("limites_minutos deve ter exatamente baixa, media e alta")
    for prioridade in PRIORIDADES:
        limite = limites[prioridade]
        if type(limite) is not int or limite < 1:
            raise ValueError(f"limite de {prioridade!r} deve ser int >= 1: {limite!r}")
    return limites


def _resumir(chamados: list[dict], limites: dict) -> dict:
    grupos = {}
    for chamado in chamados:
        grupos.setdefault(chamado["equipe"], []).append(chamado)

    equipes = []
    for nome in sorted(grupos):
        itens = grupos[nome]
        total = sum(c["duracao"] for c in itens)
        estourados = sum(1 for c in itens if c["duracao"] > limites[c["prioridade"]])
        pior = min(itens, key=lambda c: (-c["duracao"], c["id"]))
        equipes.append({
            "equipe": nome,
            "chamados": len(itens),
            "estourados": estourados,
            "tempo_medio_minutos": total // len(itens),
            "pior_id": pior["id"],
        })
    return {"equipes": equipes}


def consolidar(caminho_csv: str, caminho_sla: str, caminho_saida: str) -> dict:
    """Lê os chamados e o SLA, grava o resumo em JSON e devolve o mesmo dict."""
    chamados = _ler_chamados(caminho_csv)
    limites = _ler_sla(caminho_sla)
    resumo = _resumir(chamados, limites)
    with open(caminho_saida, "w", encoding="utf-8", newline="") as arquivo:
        arquivo.write(json.dumps(resumo, ensure_ascii=False, indent=2) + "\n")
    return resumo
