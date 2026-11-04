import csv
import json
import re
from datetime import datetime, timedelta

CABECALHO = ["id", "equipe", "aberto_em", "fechado_em", "prioridade"]
PRIORIDADES = ("baixa", "media", "alta")
PADRAO_DATA = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}")
FORMATO_DATA = "%Y-%m-%dT%H:%M"


def _ler_data(valor: str) -> datetime:
    if not PADRAO_DATA.fullmatch(valor):
        raise ValueError(f"data em formato inválido: {valor!r}")
    return datetime.strptime(valor, FORMATO_DATA)


def _ler_sla(caminho_sla: str) -> dict:
    with open(caminho_sla, encoding="utf-8") as f:
        dados = json.load(f)

    if not isinstance(dados, dict) or set(dados) != {"limites_minutos"}:
        raise ValueError("SLA deve ter exatamente a chave 'limites_minutos'")
    limites = dados["limites_minutos"]
    if not isinstance(limites, dict) or set(limites) != set(PRIORIDADES):
        raise ValueError("'limites_minutos' deve ter exatamente baixa, media e alta")
    for prioridade in PRIORIDADES:
        limite = limites[prioridade]
        if type(limite) is not int or limite < 1:
            raise ValueError(f"limite de {prioridade!r} deve ser int >= 1")
    return limites


def _ler_chamados(caminho_csv: str) -> list:
    chamados = []
    ids = set()
    try:
        with open(caminho_csv, encoding="utf-8", newline="") as f:
            leitor = csv.reader(f)
            cabecalho = next(leitor, None)
            if cabecalho != CABECALHO:
                raise ValueError(f"cabeçalho inválido: {cabecalho!r}")

            for linha in leitor:
                if all(campo.strip() == "" for campo in linha):
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
                    "duracao": (fim - inicio) // timedelta(minutes=1),
                    "prioridade": prioridade,
                })
    except csv.Error as erro:
        raise ValueError(f"CSV inválido: {erro}") from erro
    return chamados


def consolidar(caminho_csv: str, caminho_sla: str, caminho_saida: str) -> dict:
    """Lê os chamados e o SLA, grava o resumo em JSON e devolve o mesmo dict."""
    chamados = _ler_chamados(caminho_csv)
    limites = _ler_sla(caminho_sla)

    grupos = {}
    for chamado in chamados:
        grupos.setdefault(chamado["equipe"], []).append(chamado)

    equipes = []
    for nome in sorted(grupos):
        itens = grupos[nome]
        estourados = sum(1 for c in itens if c["duracao"] > limites[c["prioridade"]])
        pior = min(itens, key=lambda c: (-c["duracao"], c["id"]))
        equipes.append({
            "equipe": nome,
            "chamados": len(itens),
            "estourados": estourados,
            "tempo_medio_minutos": sum(c["duracao"] for c in itens) // len(itens),
            "pior_id": pior["id"],
        })

    resultado = {"equipes": equipes}
    with open(caminho_saida, "w", encoding="utf-8") as f:
        f.write(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n")
    return resultado
