import csv
import json
import re
from datetime import datetime, timedelta

CABECALHO = ["id", "equipe", "aberto_em", "fechado_em", "prioridade"]
PRIORIDADES = ("baixa", "media", "alta")
FORMATO_DATA = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}")


def _data(texto: str, linha: int) -> datetime:
    if not FORMATO_DATA.fullmatch(texto):
        raise ValueError(f"linha {linha}: data fora do formato YYYY-MM-DDTHH:MM: {texto!r}")
    try:
        return datetime.strptime(texto, "%Y-%m-%dT%H:%M")
    except ValueError as erro:
        raise ValueError(f"linha {linha}: data inexistente: {texto!r}") from erro


def _ler_chamados(caminho_csv: str) -> list[dict]:
    chamados = []
    ids = set()
    with open(caminho_csv, encoding="utf-8", newline="") as arq:
        try:
            leitor = csv.reader(arq)
            if next(leitor, None) != CABECALHO:
                raise ValueError("cabeçalho ausente ou diferente do esperado")
            for linha in leitor:
                campos = [campo.strip() for campo in linha]
                if not any(campos):
                    continue
                num = leitor.line_num
                if len(linha) != len(CABECALHO):
                    raise ValueError(f"linha {num}: número de colunas diferente do cabeçalho")
                id_, equipe, aberto_em, fechado_em, prioridade = campos
                if not id_:
                    raise ValueError(f"linha {num}: id vazio")
                if not equipe:
                    raise ValueError(f"linha {num}: equipe vazia")
                if id_ in ids:
                    raise ValueError(f"linha {num}: id duplicado: {id_!r}")
                if prioridade not in PRIORIDADES:
                    raise ValueError(f"linha {num}: prioridade inválida: {prioridade!r}")
                inicio = _data(aberto_em, num)
                fim = _data(fechado_em, num)
                if fim < inicio:
                    raise ValueError(f"linha {num}: fechado_em anterior a aberto_em")
                ids.add(id_)
                chamados.append({
                    "id": id_,
                    "equipe": equipe,
                    "prioridade": prioridade,
                    "duracao": (fim - inicio) // timedelta(minutes=1),
                })
        except csv.Error as erro:
            raise ValueError(f"CSV inválido: {erro}") from erro
    return chamados


def _ler_sla(caminho_sla: str) -> dict:
    with open(caminho_sla, encoding="utf-8") as arq:
        sla = json.load(arq)
    if not isinstance(sla, dict) or set(sla) != {"limites_minutos"}:
        raise ValueError("SLA deve ter exatamente a chave 'limites_minutos'")
    limites = sla["limites_minutos"]
    if not isinstance(limites, dict) or set(limites) != set(PRIORIDADES):
        raise ValueError("'limites_minutos' deve ter exatamente as prioridades baixa, media e alta")
    for prioridade in PRIORIDADES:
        limite = limites[prioridade]
        if type(limite) is not int or limite < 1:
            raise ValueError(f"limite de {prioridade!r} deve ser int >= 1")
    return limites


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
    with open(caminho_saida, "w", encoding="utf-8", newline="") as arq:
        arq.write(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n")
    return resultado
